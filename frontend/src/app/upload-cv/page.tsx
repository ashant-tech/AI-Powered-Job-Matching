'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { FIELD_LABELS } from '../../services/jobApi';

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
  const [title, setTitle] = useState('');
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');
  const [cvs, setCvs] = useState<any[]>([]);
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
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const userData = await response.json();
        // Fetch user's CVs
        const cvsResponse = await fetch(`/api/cv/user/${userData.id}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (cvsResponse.ok) {
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
        }
      }
    } catch (error) {
      console.error('Error fetching CVs:', error);
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

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      if (validTypes.includes(selectedFile.type)) {
        setFile(selectedFile);
        setMessage('');
      } else {
        setMessage('Please upload a PDF or DOCX file');
        setFile(null);
      }
    }
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
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-indigo-600">AI Job Matching</h1>
          <button
            onClick={() => router.push('/dashboard')}
            className="text-gray-600 hover:text-gray-900"
          >
            ← Back to Dashboard
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 max-w-2xl">
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-2xl font-bold mb-2">{cvs.length > 0 ? 'Update your CV' : 'Upload CV'}</h2>
          <p className="text-gray-600 mb-6">
            {cvs.length > 0 ? 'You have one CV. Upload a new file to replace it.' : 'Upload one CV to build your job-matching profile.'}
          </p>

          {message && (
            <div className={`mb-4 p-3 rounded ${message.includes('success') ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-600'}`}>
              {message}
            </div>
          )}

          <form onSubmit={handleUpload} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                CV Title
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="My Professional CV"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                CV File (PDF or DOCX)
              </label>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-indigo-500 transition">
                <input
                  type="file"
                  onChange={handleFileChange}
                  accept=".pdf,.docx"
                  className="hidden"
                  id="file-upload"
                />
                <label
                  htmlFor="file-upload"
                  className="cursor-pointer"
                >
                  <div className="text-4xl mb-2">📄</div>
                  <div className="text-gray-600">
                    {file ? file.name : 'Click to upload or drag and drop'}
                  </div>
                  <div className="text-sm text-gray-400 mt-1">
                    PDF or DOCX files only
                  </div>
                </label>
              </div>
            </div>

            <button
              type="submit"
              disabled={!file || uploading}
              className="w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {uploading ? 'Uploading...' : cvs.length > 0 ? 'Replace CV' : 'Upload CV'}
            </button>
          </form>
        </div>

        {cvs[0] && (
          <section className="mb-6 rounded-lg bg-white p-6 shadow-md">
            <h3 className="text-xl font-bold text-gray-900">Review your matching profile</h3>
            <p className="mt-1 text-sm leading-6 text-gray-600">
              CV extraction can miss details. Correct these fields to improve your personalized job matches.
            </p>
            {profileMessage && (
              <p role="status" className={`mt-4 rounded-lg p-3 text-sm ${profileMessage.includes('updated') ? 'bg-green-50 text-green-800' : 'bg-amber-50 text-amber-900'}`}>
                {profileMessage}
              </p>
            )}
            <div className="mt-5 grid gap-4 sm:grid-cols-2">
              <label className="text-sm font-medium text-gray-700">
                Main work field
                <select
                  value={editField}
                  onChange={(event) => setEditField(event.target.value)}
                  className="mt-1 w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5"
                >
                  {Object.entries(FIELD_LABELS).map(([value, label]) => (
                    <option key={value} value={value}>{label}</option>
                  ))}
                </select>
              </label>
              <label className="text-sm font-medium text-gray-700">
                Experience level
                <select
                  value={editExperienceLevel}
                  onChange={(event) => setEditExperienceLevel(event.target.value)}
                  className="mt-1 w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5"
                >
                  <option value="">Not specified</option>
                  <option value="Entry Level">Entry level</option>
                  <option value="Junior">Junior</option>
                  <option value="Mid-Level">Mid-level</option>
                  <option value="Senior">Senior</option>
                </select>
              </label>
              <label className="text-sm font-medium text-gray-700">
                Years of experience
                <input
                  type="number"
                  min="0"
                  max="60"
                  value={editYears}
                  onChange={(event) => setEditYears(event.target.value)}
                  className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2.5"
                />
              </label>
              <label className="text-sm font-medium text-gray-700 sm:col-span-2">
                Skills (separate with commas)
                <textarea
                  value={editSkills}
                  onChange={(event) => setEditSkills(event.target.value)}
                  rows={3}
                  className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2.5"
                  placeholder="Python, project management, accounting"
                />
              </label>
              <label className="text-sm font-medium text-gray-700">
                Previous job titles (one per line)
                <textarea
                  value={editJobTitles}
                  onChange={(event) => setEditJobTitles(event.target.value)}
                  rows={3}
                  className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2.5"
                  placeholder={'Software Developer\nIT Support Specialist'}
                />
              </label>
              <label className="text-sm font-medium text-gray-700">
                Education (one entry per line: degree | field | institution | year)
                <textarea
                  value={editEducation}
                  onChange={(event) => setEditEducation(event.target.value)}
                  rows={3}
                  className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2.5"
                  placeholder="BSc | Computer Science | Example University | 2022"
                />
              </label>
            </div>
            <button
              type="button"
              onClick={handleSaveProfile}
              disabled={savingProfile}
              className="mt-4 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {savingProfile ? 'Saving and refreshing matches...' : 'Save profile and refresh matches'}
            </button>
          </section>
        )}

        {/* Existing CVs */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold mb-4">Your CV</h3>
          {cvs.length === 0 ? (
            <p className="text-gray-600">No CVs uploaded yet</p>
          ) : (
            <div className="space-y-4">
              {cvs.map((cv) => (
                <div key={cv.id} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h4 className="font-semibold">{cv.title}</h4>
                      <p className="text-sm text-gray-600">
                        Uploaded: {new Date(cv.created_at).toLocaleDateString()}
                      </p>

                      {/* Enhanced CV Analysis Display */}
                      <div className="mt-3 space-y-2">
                        {cv.experience_level && (
                          <div className="flex items-center gap-2">
                            <span className="text-sm text-gray-600">Experience Level:</span>
                            <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded text-xs font-semibold">
                              {cv.experience_level}
                            </span>
                          </div>
                        )}

                        {cv.total_years_experience !== undefined && cv.total_years_experience !== null && (
                          <div className="flex items-center gap-2">
                            <span className="text-sm text-gray-600">Total Experience:</span>
                            <span className="text-sm font-medium text-gray-800">
                              {cv.total_years_experience}+ years
                            </span>
                          </div>
                        )}

                        {cv.skills && (
                          <div>
                            <span className="text-sm text-gray-600">Skills extracted: </span>
                            <span className="text-sm font-medium text-gray-800">
                              {parseList(cv.skills).length}
                            </span>
                            <div className="flex flex-wrap gap-1 mt-1">
                              {parseList(cv.skills).slice(0, 5).map((skill: string, index: number) => (
                                <span key={index} className="bg-gray-100 text-gray-700 px-2 py-0.5 rounded text-xs">
                                  {skill}
                                </span>
                              ))}
                              {parseList(cv.skills).length > 5 && (
                                <span className="text-xs text-gray-500">+{parseList(cv.skills).length - 5} more</span>
                              )}
                            </div>
                          </div>
                        )}

                        {cv.job_titles && (
                          <div>
                            <span className="text-sm text-gray-600">Job Titles: </span>
                            <span className="text-sm font-medium text-gray-800">
                              {parseList(cv.job_titles).join(', ') || 'Not specified'}
                            </span>
                          </div>
                        )}

                        {cv.field && FIELD_LABELS[cv.field] && (
                          <div className="mt-2">
                            <span className="bg-purple-100 text-purple-800 px-2 py-0.5 rounded-full text-xs font-semibold">
                              Detected field: {FIELD_LABELS[cv.field]}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                    <button
                      onClick={() => handleAnalyze(cv.id)}
                      className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700 transition whitespace-nowrap"
                    >
                      Reanalyze
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
