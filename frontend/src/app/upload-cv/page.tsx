'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { FIELD_LABELS } from '../../services/jobApi';

const MAX_CV_SIZE = 10 * 1024 * 1024;

function parseList(value?: string): string[] {
  if (!value) return [];
  try {
    const parsed = JSON.parse(value);
    return Array.isArray(parsed) ? parsed.filter((item): item is string => typeof item === 'string') : [];
  } catch {
    return value.split(/[,;\n]/).map((item) => item.trim()).filter(Boolean);
  }
}

function parseEducation(value?: string): string[] {
  if (!value) return [];
  try {
    const parsed = JSON.parse(value);
    if (!Array.isArray(parsed)) return [];
    return parsed.map((entry) => {
      if (typeof entry === 'string') return entry;
      return [entry.degree, entry.field, entry.institution, entry.year].filter(Boolean).join(' | ');
    }).filter(Boolean);
  } catch {
    return [];
  }
}

export default function UploadCVPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [title, setTitle] = useState('');
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');
  const [cvs, setCvs] = useState<any[]>([]);
  const [loadingCVs, setLoadingCVs] = useState(true);
  const [cvLoadError, setCvLoadError] = useState('');
  const [editSkills, setEditSkills] = useState('');
  const [editField, setEditField] = useState('other');
  const [editExperienceLevel, setEditExperienceLevel] = useState('');
  const [editYears, setEditYears] = useState('');
  const [editJobTitles, setEditJobTitles] = useState('');
  const [editEducation, setEditEducation] = useState('');
  const [savingProfile, setSavingProfile] = useState(false);
  const [profileMessage, setProfileMessage] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    fetchCVs();
  }, [router]);

  const fetchCVs = async () => {
    setLoadingCVs(true);
    setCvLoadError('');
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Could not load your account (HTTP ${response.status})`);
      }
      const userData = await response.json();
      const cvsResponse = await fetch(`/api/cv/user/${userData.id}`, {
        headers: {
            'Authorization': `Bearer ${token}`,
          },
      });

      if (!cvsResponse.ok) {
        throw new Error(`Could not load your CVs (HTTP ${cvsResponse.status})`);
      }
      const cvsData = await cvsResponse.json();
      setCvs(cvsData);
      const cv = cvsData[0];
      if (cv) {
        setEditSkills(parseList(cv.skills).join(', '));
        setEditField(cv.field || 'other');
        setEditExperienceLevel(cv.experience_level === 'Not specified' ? '' : cv.experience_level || '');
        setEditYears(cv.total_years_experience === null || cv.total_years_experience === undefined
          ? ''
          : String(cv.total_years_experience));
        setEditJobTitles(parseList(cv.job_titles).join('\n'));
        setEditEducation(parseEducation(cv.education).join('\n'));
      }
    } catch (error) {
      console.error('Error fetching CVs:', error);
      setCvLoadError(error instanceof Error ? error.message : 'Could not load your CV information.');
    } finally {
      setLoadingCVs(false);
    }
  };

  const handleSaveProfile = async () => {
    const cv = cvs[0];
    const token = localStorage.getItem('token');
    if (!cv || !token) return;

    setSavingProfile(true);
    setProfileMessage('');
    try {
      const response = await fetch(`/api/cv/${cv.id}/profile`, {
        method: 'PATCH',
        headers: {
          Authorization: 'Bearer ' + token,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          skills: editSkills.split(/[,;\n]/).map((skill) => skill.trim()).filter(Boolean),
          field: editField,
          experience_level: editExperienceLevel || null,
          total_years_experience: editYears === '' ? null : Number(editYears),
          job_titles: editJobTitles.split('\n').map((title) => title.trim()).filter(Boolean),
          education: editEducation.split('\n').map((line) => {
            const [degree = '', field = '', institution = '', year = ''] = line.split('|').map((part) => part.trim());
            return { degree, field, institution, year };
          }).filter((entry) => Object.values(entry).some(Boolean)),
        }),
      });
      if (!response.ok) {
        const errorBody = await response.text();
        let errorMessage = `Could not save CV profile (HTTP ${response.status})`;
        try {
          const errorData = JSON.parse(errorBody);
          if (typeof errorData.detail === 'string') errorMessage = errorData.detail;
        } catch {}
        throw new Error(errorMessage);
      }

      await response.json();
      const matchingResponse = await fetch(`/api/matching/cv/${cv.id}`, {
        method: 'POST',
        headers: { Authorization: 'Bearer ' + token },
      });
      if (!matchingResponse.ok) {
        const errorBody = await matchingResponse.text();
        throw new Error(`Profile saved, but matches could not be refreshed (HTTP ${matchingResponse.status}): ${errorBody}`);
      }
      await fetchCVs();
      setProfileMessage('Profile updated and your matches were refreshed.');
    } catch (error) {
      setProfileMessage(error instanceof Error ? error.message : 'Could not update your CV profile.');
    } finally {
      setSavingProfile(false);
    }
  };

  const selectFile = (selectedFile?: File) => {
    if (!selectedFile) return;
    const extension = selectedFile.name.split('.').pop()?.toLowerCase();
    if (extension !== 'pdf' && extension !== 'docx') {
      setMessage('Choose a PDF or DOCX file to continue.');
      setFile(null);
      return;
    }
    if (selectedFile.size > MAX_CV_SIZE) {
      setMessage('Your file is larger than 10 MB. Choose a smaller CV file.');
      setFile(null);
      return;
    }

    setFile(selectedFile);
    setMessage('');
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    selectFile(e.target.files?.[0]);
    e.target.value = '';
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    selectFile(e.dataTransfer.files?.[0]);
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!file) {
      setMessage('Please select a file to upload');
      return;
    }

    setUploading(true);
    setMessage('');

    try {
      const token = localStorage.getItem('token');
      const formData = new FormData();
      formData.append('file', file);
      formData.append('title', title || file.name);

      const response = await fetch('/api/cv/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (response.ok) {
        const cvData = await response.json();
        const fieldLabel = cvData.field && cvData.field !== 'other' ? FIELD_LABELS[cvData.field] : null;
        const base = cvs.length > 0 ? 'CV replaced successfully!' : 'CV uploaded successfully!';
        setMessage(fieldLabel ? `${base} Detected field: ${fieldLabel} — we'll match you with ${fieldLabel} jobs.` : base);
        setFile(null);
        setTitle('');
        fetchCVs();

        // Automatically redirect to recommendations page after successful upload
        setTimeout(() => {
          router.push('/recommendations');
        }, 1500);
      } else {
        const responseBody = await response.text();
        let errorMessage = `Upload failed (HTTP ${response.status})`;
        try {
          const errorData = JSON.parse(responseBody);
          if (typeof errorData.detail === 'string') {
            errorMessage = errorData.detail;
          }
        } catch {}
        setMessage(errorMessage);
      }
    } catch (error) {
      setMessage(error instanceof Error ? `Error uploading CV: ${error.message}` : 'Error uploading CV');
    } finally {
      setUploading(false);
    }
  };

  const handleAnalyze = async (cvId: number) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/cv/${cvId}/analyze`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        setMessage('CV analysis complete!');
        fetchCVs();
      } else {
        setMessage('Analysis failed');
      }
    } catch (error) {
      setMessage('Error analyzing CV');
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/95 shadow-sm backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
          <button onClick={() => router.push('/dashboard')} className="flex items-center gap-3 text-left">
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600 text-white shadow-sm">
              <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
                <rect x="3" y="7" width="18" height="13" rx="2.5" />
                <path d="M8 7V5.5A1.5 1.5 0 0 1 9.5 4h5A1.5 1.5 0 0 1 16 5.5V7M3 12h18m-11 0v2h4v-2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </span>
            <span className="text-base font-bold tracking-tight sm:text-lg">AI Job Matching</span>
          </button>
          <button
            onClick={() => router.push('/dashboard')}
            className="rounded-lg px-3 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100 hover:text-slate-900"
          >
            <span aria-hidden="true">← </span>Dashboard
          </button>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-7 sm:px-6 sm:py-10 lg:px-8">
        <section className="relative mb-7 overflow-hidden rounded-3xl bg-gradient-to-br from-slate-950 via-indigo-950 to-indigo-800 px-6 py-8 text-white shadow-lg shadow-indigo-950/10 sm:px-9 sm:py-10">
          <div aria-hidden="true" className="absolute -right-16 -top-28 h-72 w-72 rounded-full border-[32px] border-white/[0.06]" />
          <div aria-hidden="true" className="absolute -bottom-32 right-1/3 h-64 w-64 rounded-full border-[26px] border-white/[0.04]" />
          <div className="relative grid gap-8 lg:grid-cols-[1fr,auto] lg:items-end">
            <div className="max-w-2xl">
              <p className="text-sm font-semibold text-indigo-200">Your career starts here</p>
              <h1 className="mt-2 text-3xl font-semibold tracking-tight sm:text-4xl">
                {cvs.length > 0 ? 'Refresh your CV profile' : 'Let your experience find its next opportunity'}
              </h1>
              <p className="mt-3 max-w-xl text-sm leading-6 text-indigo-100/80 sm:text-base">
                Add your CV and we’ll identify your skills, experience, and career field to find more relevant job matches.
              </p>
            </div>
            <div className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/[0.08] px-4 py-3 backdrop-blur">
              <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-400/15 text-emerald-200">
                <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
                  <path d="M12 3 5 6v5c0 4.6 2.9 8.1 7 10 4.1-1.9 7-5.4 7-10V6l-7-3Z" strokeLinejoin="round" />
                  <path d="m9 12 2 2 4-4" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </span>
              <div>
                <p className="text-sm font-semibold">Private and secure</p>
                <p className="mt-0.5 text-xs text-indigo-100/75">Only used to personalize your matches</p>
              </div>
            </div>
          </div>
          <div className="relative mt-8 grid gap-3 border-t border-white/10 pt-5 sm:grid-cols-3">
            {[
              ['01', 'Upload your CV', 'PDF or DOCX, up to 10 MB'],
              ['02', 'Review your profile', 'Check your extracted skills'],
              ['03', 'Explore better matches', 'See roles tailored to you'],
            ].map(([number, titleText, description]) => (
              <div key={number} className="flex items-start gap-3">
                <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-white/10 text-xs font-bold text-indigo-100">{number}</span>
                <div>
                  <p className="text-sm font-semibold text-white">{titleText}</p>
                  <p className="mt-1 text-xs leading-5 text-indigo-100/70">{description}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {cvLoadError && (
          <div role="alert" className="mb-6 flex flex-col gap-3 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800 sm:flex-row sm:items-center sm:justify-between">
            <span>{cvLoadError}</span>
            <button onClick={() => fetchCVs()} className="font-semibold underline underline-offset-2">Try again</button>
          </div>
        )}

        <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,1.35fr),minmax(280px,0.75fr)]">
          <section className="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">
            <div className="border-b border-slate-100 px-5 py-5 sm:px-7">
              <div className="flex items-start gap-4">
                <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-indigo-50 text-indigo-600">
                  <svg viewBox="0 0 24 24" fill="none" className="h-6 w-6" stroke="currentColor" strokeWidth="1.7" aria-hidden="true">
                    <path d="M7 3.5h7l4 4V20a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4.5a1 1 0 0 1 1-1Z" strokeLinejoin="round" />
                    <path d="M14 4v4h4m-9 5h6m-6 3h6" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </span>
                <div>
                  <h2 className="text-xl font-semibold tracking-tight text-slate-950">
                    {cvs.length > 0 ? 'Replace your CV' : 'Upload your CV'}
                  </h2>
                  <p className="mt-1 text-sm leading-6 text-slate-500">
                    {cvs.length > 0 ? 'Uploading a new file will update your matching profile.' : 'Start with your latest resume so we can build a more accurate profile.'}
                  </p>
                </div>
              </div>
            </div>

            <form onSubmit={handleUpload} className="space-y-5 p-5 sm:p-7">
              {message && (
                <div role={message.toLowerCase().includes('success') || message.toLowerCase().includes('complete') ? 'status' : 'alert'}
                  className={`flex items-start gap-3 rounded-xl border px-4 py-3 text-sm leading-6 ${
                    message.toLowerCase().includes('success') || message.toLowerCase().includes('complete')
                      ? 'border-emerald-200 bg-emerald-50 text-emerald-800'
                      : 'border-red-200 bg-red-50 text-red-800'
                  }`}>
                  <span className="mt-0.5 font-bold" aria-hidden="true">{message.toLowerCase().includes('success') ? '✓' : '!'}</span>
                  <span>{message}</span>
                </div>
              )}

              <label className="block">
                <span className="mb-2 block text-sm font-semibold text-slate-700">Give this CV a name <span className="font-normal text-slate-400">(optional)</span></span>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-indigo-400 focus:ring-4 focus:ring-indigo-500/10"
                  placeholder="e.g. Product Designer CV"
                  maxLength={100}
                />
              </label>

              <div>
                <p className="mb-2 block text-sm font-semibold text-slate-700">Choose your CV file</p>
                <div
                  onDragEnter={(event) => { event.preventDefault(); setIsDragging(true); }}
                  onDragOver={(event) => { event.preventDefault(); setIsDragging(true); }}
                  onDragLeave={(event) => {
                    if (!event.currentTarget.contains(event.relatedTarget as Node | null)) setIsDragging(false);
                  }}
                  onDrop={handleDrop}
                  className={`relative rounded-2xl border-2 border-dashed p-6 text-center transition sm:p-8 ${
                    isDragging ? 'border-indigo-500 bg-indigo-50' : file ? 'border-emerald-300 bg-emerald-50/60' : 'border-slate-300 bg-slate-50/70 hover:border-indigo-400 hover:bg-indigo-50/50'
                  }`}
                >
                  <input
                    type="file"
                    onChange={handleFileChange}
                    accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    className="sr-only"
                    id="file-upload"
                    aria-label="Choose a PDF or DOCX CV file"
                  />
                  {file ? (
                    <div className="mx-auto flex max-w-lg items-center gap-4 rounded-xl border border-emerald-100 bg-white p-4 text-left shadow-sm">
                      <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-emerald-50 text-emerald-700">
                        <svg viewBox="0 0 24 24" fill="none" className="h-6 w-6" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
                          <path d="M7 3.5h7l4 4V20a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4.5a1 1 0 0 1 1-1Z" strokeLinejoin="round" />
                          <path d="M14 4v4h4m-9 5 2 2 4-4" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                      </span>
                      <span className="min-w-0 flex-1">
                        <span className="block truncate text-sm font-semibold text-slate-900">{file.name}</span>
                        <span className="mt-1 block text-xs text-slate-500">{(file.size / (1024 * 1024)).toFixed(2)} MB · Ready to upload</span>
                      </span>
                      <button
                        type="button"
                        onClick={() => { setFile(null); setMessage(''); }}
                        className="rounded-lg px-3 py-2 text-xs font-semibold text-slate-500 transition hover:bg-slate-100 hover:text-slate-900"
                      >
                        Remove
                      </button>
                    </div>
                  ) : (
                    <>
                      <span className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-white text-indigo-600 shadow-sm ring-1 ring-slate-200">
                        <svg viewBox="0 0 24 24" fill="none" className="h-7 w-7" stroke="currentColor" strokeWidth="1.7" aria-hidden="true">
                          <path d="M12 16V4m0 0L7.5 8.5M12 4l4.5 4.5M5 14v4.5A1.5 1.5 0 0 0 6.5 20h11a1.5 1.5 0 0 0 1.5-1.5V14" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                      </span>
                      <p className="mt-4 text-sm font-semibold text-slate-900">
                        Drop your CV here or{' '}
                        <label htmlFor="file-upload" className="cursor-pointer text-indigo-600 underline decoration-indigo-300 underline-offset-4 hover:text-indigo-700">browse files</label>
                      </p>
                      <p className="mt-2 text-xs text-slate-500">PDF or DOCX · Maximum file size 10 MB</p>
                    </>
                  )}
                </div>
              </div>

              <button
                type="submit"
                disabled={!file || uploading}
                className="flex w-full items-center justify-center gap-2 rounded-xl bg-indigo-600 px-5 py-3.5 text-sm font-semibold text-white shadow-sm shadow-indigo-600/20 transition hover:bg-indigo-700 focus:outline-none focus:ring-4 focus:ring-indigo-500/20 disabled:cursor-not-allowed disabled:bg-slate-300 disabled:shadow-none"
              >
                {uploading && <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white" />}
                {uploading ? 'Uploading your CV...' : cvs.length > 0 ? 'Replace CV and refresh matches' : 'Upload CV and find matches'}
              </button>
              <p className="text-center text-xs leading-5 text-slate-400">Your file is securely processed to create your personalized job matches.</p>
            </form>
          </section>

          <aside className="space-y-5">
            <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-sm font-semibold text-slate-900">Your CV status</p>
                  <p className="mt-1 text-xs text-slate-500">Profile used for matching</p>
                </div>
                <span className={`rounded-full px-3 py-1 text-xs font-semibold ${cvs.length ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'}`}>
                  {cvs.length ? 'CV added' : 'Not uploaded'}
                </span>
              </div>

              {loadingCVs ? (
                <div role="status" className="mt-5 flex items-center gap-3 rounded-xl bg-slate-50 p-4 text-sm text-slate-500">
                  <span className="h-4 w-4 animate-spin rounded-full border-2 border-indigo-200 border-t-indigo-600" />
                  Checking your CV...
                </div>
              ) : cvs.length ? (
                cvs.map((cv) => (
                  <div key={cv.id} className="mt-5 rounded-2xl bg-slate-50 p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex min-w-0 items-start gap-3">
                        <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-white text-indigo-600 ring-1 ring-slate-200">
                          <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
                            <path d="M7 3.5h7l4 4V20a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4.5a1 1 0 0 1 1-1Z" strokeLinejoin="round" />
                            <path d="M14 4v4h4" strokeLinecap="round" strokeLinejoin="round" />
                          </svg>
                        </span>
                        <div className="min-w-0">
                          <h3 className="break-words text-sm font-semibold text-slate-900">{cv.title || cv.file_name || 'My CV'}</h3>
                          <p className="mt-1 text-xs text-slate-500">
                            {cv.created_at ? `Added ${new Date(cv.created_at).toLocaleDateString()}` : 'Ready for matching'}
                          </p>
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={() => handleAnalyze(cv.id)}
                        className="shrink-0 rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-600 transition hover:border-indigo-200 hover:text-indigo-700"
                      >
                        Reanalyze
                      </button>
                    </div>

                    <div className="mt-4 flex flex-wrap gap-2">
                      {cv.field && cv.field !== 'other' && FIELD_LABELS[cv.field] && (
                        <span className="rounded-full bg-indigo-100 px-3 py-1 text-xs font-semibold text-indigo-700">{FIELD_LABELS[cv.field]}</span>
                      )}
                      {cv.experience_level && cv.experience_level !== 'Not specified' && (
                        <span className="rounded-full bg-white px-3 py-1 text-xs font-medium text-slate-600 ring-1 ring-slate-200">{cv.experience_level}</span>
                      )}
                      {cv.total_years_experience !== null && cv.total_years_experience !== undefined && (
                        <span className="rounded-full bg-white px-3 py-1 text-xs font-medium text-slate-600 ring-1 ring-slate-200">{cv.total_years_experience} years experience</span>
                      )}
                    </div>

                    {parseList(cv.skills).length > 0 && (
                      <div className="mt-4 border-t border-slate-200 pt-4">
                        <p className="text-xs font-semibold text-slate-600">{parseList(cv.skills).length} skills found</p>
                        <div className="mt-2 flex flex-wrap gap-1.5">
                          {parseList(cv.skills).slice(0, 6).map((skill: string, index: number) => (
                            <span key={`${skill}-${index}`} className="rounded-md bg-white px-2 py-1 text-xs text-slate-600 ring-1 ring-slate-200">{skill}</span>
                          ))}
                          {parseList(cv.skills).length > 6 && (
                            <span className="px-1 py-1 text-xs text-slate-500">+{parseList(cv.skills).length - 6} more</span>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="mt-5 rounded-2xl border border-dashed border-slate-200 bg-slate-50 p-5 text-center">
                  <p className="text-sm font-medium text-slate-700">Your profile is waiting for a CV</p>
                  <p className="mt-1 text-xs leading-5 text-slate-500">Upload one to see your career field and extracted skills here.</p>
                </div>
              )}
            </section>

            <section className="rounded-3xl border border-indigo-100 bg-indigo-50/70 p-5 sm:p-6">
              <p className="text-sm font-semibold text-indigo-950">Get the best matches</p>
              <ul className="mt-3 space-y-3 text-sm leading-5 text-indigo-900/75">
                {[
                  'Use your latest CV with clear job titles and dates.',
                  'Include the skills and tools you use most.',
                  'Review the extracted profile below and correct anything missing.',
                ].map((tip) => (
                  <li key={tip} className="flex gap-2.5">
                    <span className="mt-0.5 text-indigo-600" aria-hidden="true">✓</span>
                    <span>{tip}</span>
                  </li>
                ))}
              </ul>
            </section>
          </aside>
        </div>

        {cvs[0] && (
          <section className="mt-6 overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">
            <div className="flex flex-col gap-4 border-b border-slate-100 bg-gradient-to-r from-indigo-50/70 to-white p-5 sm:flex-row sm:items-center sm:justify-between sm:p-7">
              <div className="flex items-start gap-4">
                <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-indigo-100 text-indigo-700">
                  <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
                    <path d="M12 3v3m0 12v3m9-9h-3M6 12H3m12.4-6.4-2.1 2.1M7.7 16.3l-2.1 2.1m12.8 0-2.1-2.1M7.7 7.7 5.6 5.6M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </span>
                <div>
                  <p className="text-sm font-semibold text-indigo-700">Personalize your results</p>
                  <h2 className="mt-1 text-xl font-semibold tracking-tight text-slate-950">Review your matching profile</h2>
                  <p className="mt-1 max-w-2xl text-sm leading-6 text-slate-500">Extraction is a starting point. Correct these details to help us recommend roles that fit you better.</p>
                </div>
              </div>
            </div>
            <div className="p-5 sm:p-7">
              {profileMessage && (
                <p role="status" className={`mb-5 rounded-xl border px-4 py-3 text-sm leading-6 ${
                  profileMessage.includes('updated') ? 'border-emerald-200 bg-emerald-50 text-emerald-800' : 'border-amber-200 bg-amber-50 text-amber-900'
                }`}>
                  {profileMessage}
                </p>
              )}
              <div className="grid gap-x-5 gap-y-5 sm:grid-cols-2">
                <label className="text-sm font-semibold text-slate-700">
                  Main work field
                  <select
                    value={editField}
                    onChange={(event) => setEditField(event.target.value)}
                    className="mt-2 w-full rounded-xl border border-slate-200 bg-white px-3.5 py-3 text-sm font-normal text-slate-800 outline-none transition focus:border-indigo-400 focus:ring-4 focus:ring-indigo-500/10"
                  >
                    {Object.entries(FIELD_LABELS).map(([value, label]) => (
                      <option key={value} value={value}>{label}</option>
                    ))}
                  </select>
                </label>
                <label className="text-sm font-semibold text-slate-700">
                  Experience level
                  <select
                    value={editExperienceLevel}
                    onChange={(event) => setEditExperienceLevel(event.target.value)}
                    className="mt-2 w-full rounded-xl border border-slate-200 bg-white px-3.5 py-3 text-sm font-normal text-slate-800 outline-none transition focus:border-indigo-400 focus:ring-4 focus:ring-indigo-500/10"
                  >
                    <option value="">Not specified</option>
                    <option value="Entry Level">Entry level</option>
                    <option value="Junior">Junior</option>
                    <option value="Mid-Level">Mid-level</option>
                    <option value="Senior">Senior</option>
                  </select>
                </label>
                <label className="text-sm font-semibold text-slate-700">
                  Years of experience
                  <input
                    type="number"
                    min="0"
                    max="60"
                    value={editYears}
                    onChange={(event) => setEditYears(event.target.value)}
                    className="mt-2 w-full rounded-xl border border-slate-200 px-3.5 py-3 text-sm font-normal text-slate-800 outline-none transition focus:border-indigo-400 focus:ring-4 focus:ring-indigo-500/10"
                    placeholder="e.g. 4"
                  />
                </label>
                <label className="text-sm font-semibold text-slate-700">
                  Skills <span className="font-normal text-slate-400">(separate with commas)</span>
                  <textarea
                    value={editSkills}
                    onChange={(event) => setEditSkills(event.target.value)}
                    rows={3}
                    className="mt-2 w-full rounded-xl border border-slate-200 px-3.5 py-3 text-sm font-normal text-slate-800 outline-none transition focus:border-indigo-400 focus:ring-4 focus:ring-indigo-500/10"
                    placeholder="Python, project management, accounting"
                  />
                </label>
                <label className="text-sm font-semibold text-slate-700">
                  Previous job titles <span className="font-normal text-slate-400">(one per line)</span>
                  <textarea
                    value={editJobTitles}
                    onChange={(event) => setEditJobTitles(event.target.value)}
                    rows={3}
                    className="mt-2 w-full rounded-xl border border-slate-200 px-3.5 py-3 text-sm font-normal text-slate-800 outline-none transition focus:border-indigo-400 focus:ring-4 focus:ring-indigo-500/10"
                    placeholder={'Software Developer\nIT Support Specialist'}
                  />
                </label>
                <label className="text-sm font-semibold text-slate-700">
                  Education <span className="font-normal text-slate-400">(one entry per line)</span>
                  <textarea
                    value={editEducation}
                    onChange={(event) => setEditEducation(event.target.value)}
                    rows={3}
                    className="mt-2 w-full rounded-xl border border-slate-200 px-3.5 py-3 text-sm font-normal text-slate-800 outline-none transition focus:border-indigo-400 focus:ring-4 focus:ring-indigo-500/10"
                    placeholder="BSc | Computer Science | Example University | 2022"
                  />
                  <span className="mt-1 block text-xs font-normal text-slate-400">Format: degree | field | institution | year</span>
                </label>
              </div>
              <div className="mt-6 flex flex-col gap-3 border-t border-slate-100 pt-5 sm:flex-row sm:items-center sm:justify-between">
                <p className="text-xs leading-5 text-slate-500">Saving your profile also refreshes your job recommendations.</p>
                <button
                  type="button"
                  onClick={handleSaveProfile}
                  disabled={savingProfile}
                  className="inline-flex items-center justify-center gap-2 rounded-xl bg-indigo-600 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700 focus:outline-none focus:ring-4 focus:ring-indigo-500/20 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {savingProfile && <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white" />}
                  {savingProfile ? 'Saving and refreshing matches...' : 'Save profile and refresh matches'}
                </button>
              </div>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
