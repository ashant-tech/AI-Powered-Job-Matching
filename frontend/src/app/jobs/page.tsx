'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { jobApi, FIELD_LABELS, ETHIOPIAN_CITIES } from '../../services/jobApi';

export default function JobsPage() {
  const router = useRouter();
  const [jobs, setJobs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [appliedSearchTerm, setAppliedSearchTerm] = useState('');
  const [searchError, setSearchError] = useState('');
  const [refreshKey, setRefreshKey] = useState(0);
  const [locationFilter, setLocationFilter] = useState('');
  const [jobTypeFilter, setJobTypeFilter] = useState('');
  const [fieldFilter, setFieldFilter] = useState('');
  const [remoteOnly, setRemoteOnly] = useState(false);
  const [salaryMin, setSalaryMin] = useState('');
  const [salaryMax, setSalaryMax] = useState('');
  const [deadlineDays, setDeadlineDays] = useState('');
  const [forYou, setForYou] = useState(false);
  const [token, setToken] = useState<string | null>(null);
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    setToken(storedToken);
    if (storedToken) {
      loadDefaultField(storedToken);
    }
  }, []);

  // Pre-select the logged-in user's CV-detected field so the default browse
  // shows jobs relevant to them; they can switch to "All Fields" to see all.
  const loadDefaultField = async (authToken: string) => {
    try {
      const meRes = await fetch('/api/auth/me', {
        headers: { Authorization: `Bearer ${authToken}` },
      });
      if (!meRes.ok) return;
      const me = await meRes.json();
      const cvRes = await fetch(`/api/cv/user/${me.id}`, {
        headers: { Authorization: `Bearer ${authToken}` },
      });
      if (!cvRes.ok) return;
      const cvs = await cvRes.json();
      const detected = (cvs || []).find((c: any) => c.field && c.field !== 'other');
      if (detected?.field) {
        setFieldFilter(detected.field);
      }
    } catch {
      // If we can't load the field, fall back to showing all jobs.
    }
  };

  useEffect(() => {
    const controller = new AbortController();
    const fetchJobs = async () => {
      setLoading(true);
      setSearchError('');
      try {
        if (forYou && token) {
          const recommended = await jobApi.getRecommendedJobs(token, 50, controller.signal);
          setJobs(recommended);
          return;
        }

        const params = new URLSearchParams();
        if (appliedSearchTerm.trim()) params.set('search', appliedSearchTerm.trim());
        if (locationFilter.trim()) params.set('location', locationFilter.trim());
        if (jobTypeFilter) params.set('job_type', jobTypeFilter);
        if (fieldFilter) params.set('field', fieldFilter);
        if (remoteOnly) params.set('remote_only', 'true');
        if (salaryMin) params.set('salary_min', salaryMin);
        if (salaryMax) params.set('salary_max', salaryMax);
        if (deadlineDays) params.set('deadline_days', deadlineDays);

        const query = params.toString();
        const response = await fetch(`/api/jobs/${query ? `?${query}` : ''}`, {
          signal: controller.signal,
        });
        if (!response.ok) {
          throw new Error('Could not load jobs. Please try again.');
        }
        setJobs(await response.json());
      } catch (error) {
        if (controller.signal.aborted) return;
        setJobs([]);
        setSearchError(error instanceof Error ? error.message : 'Could not load jobs. Please try again.');
      } finally {
        if (!controller.signal.aborted) setLoading(false);
      }
    };

    fetchJobs();
    return () => controller.abort();
  }, [
    appliedSearchTerm,
    deadlineDays,
    fieldFilter,
    forYou,
    jobTypeFilter,
    locationFilter,
    remoteOnly,
    refreshKey,
    salaryMax,
    salaryMin,
    token,
  ]);

  const handleSearch = () => setAppliedSearchTerm(searchTerm);

  const clearFilters = () => {
    setSearchTerm('');
    setAppliedSearchTerm('');
    setLocationFilter('');
    setJobTypeFilter('');
    setFieldFilter('');
    setRemoteOnly(false);
    setSalaryMin('');
    setSalaryMax('');
    setDeadlineDays('');
    setForYou(false);
  };

  const formatSalary = (salary: number) => {
    return `${salary.toLocaleString()} ETB`;
  };

  const getDeadlineDisplay = (deadline: string) => {
    const days = Math.ceil((new Date(deadline).getTime() - Date.now()) / (1000 * 60 * 60 * 24));
    if (days <= 0) return { text: 'Closed', urgent: true };
    if (days === 1) return { text: 'Apply by tomorrow', urgent: true };
    if (days <= 7) return { text: `Apply by ${new Date(deadline).toLocaleDateString()} (${days} days left)`, urgent: true };
    return { text: `Apply by ${new Date(deadline).toLocaleDateString()}`, urgent: false };
  };

  const getActiveFiltersCount = () => {
    let count = 0;
    if (appliedSearchTerm) count++;
    if (locationFilter) count++;
    if (jobTypeFilter) count++;
    if (fieldFilter) count++;
    if (remoteOnly) count++;
    if (salaryMin) count++;
    if (salaryMax) count++;
    if (deadlineDays) count++;
    return count;
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      {/* Header */}
      <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/95 shadow-sm backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
          <Link href="/" className="flex items-center gap-3 text-slate-900">
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600 text-white shadow-sm">
              <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
                <rect x="3" y="7" width="18" height="13" rx="2.5" />
                <path d="M8 7V5.5A1.5 1.5 0 0 1 9.5 4h5A1.5 1.5 0 0 1 16 5.5V7M3 12h18m-11 0v2h4v-2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </span>
            <span className="text-base font-bold tracking-tight sm:text-lg">AI Job Matching</span>
          </Link>
          <nav aria-label="Main navigation" className="flex items-center gap-2 sm:gap-4">
            {token ? (
              <button
                onClick={() => router.push('/dashboard')}
                className="rounded-lg px-3 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100 hover:text-slate-900"
              >
                Dashboard
              </button>
            ) : (
              <>
                <Link href="/login" className="rounded-lg px-3 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100 hover:text-slate-900">Sign in</Link>
                <Link href="/register" className="rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700">Create account</Link>
              </>
            )}
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 sm:py-10 lg:px-8">
        <div className="mb-7">
          <p className="text-sm font-semibold text-indigo-600">Explore opportunities</p>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight text-slate-950 sm:text-4xl">Find your next opportunity</h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600 sm:text-base">
            Search current listings by role, location, and field. Sign in to see recommendations tailored to your profile.
          </p>
        </div>

        {/* Search and Filters */}
        <div className="mb-7 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-6">
          {token && (
            <div className="mb-5 flex flex-col gap-3 border-b border-slate-100 pb-5 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 className="font-semibold text-slate-900">Personalized search</h2>
                <p className="mt-1 text-sm text-slate-500">Use your profile to find roles that fit your skills.</p>
              </div>
              <button
                onClick={() => setForYou(!forYou)}
                className={`inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold transition focus:outline-none focus:ring-4 focus:ring-indigo-500/15 ${
                  forYou
                    ? 'bg-indigo-600 text-white shadow-sm hover:bg-indigo-700'
                    : 'border border-indigo-200 bg-indigo-50 text-indigo-700 hover:bg-indigo-100'
                }`}
              >
                <svg viewBox="0 0 24 24" fill="none" className="h-4 w-4" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
                  <path d="M12 3.5 14.6 9l5.9.8-4.3 4.1 1 5.8-5.2-2.8-5.2 2.8 1-5.8-4.3-4.1 5.9-.8L12 3.5Z" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                {forYou ? 'Showing jobs for you' : 'Show jobs for you'}
              </button>
            </div>
          )}

          {/* Basic Filters */}
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-[1.35fr_1fr_1fr_1fr_auto]">
            <div className="relative">
              <svg viewBox="0 0 24 24" fill="none" className="pointer-events-none absolute left-3.5 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
                <circle cx="10.8" cy="10.8" r="6.8" />
                <path d="m16 16 4 4" strokeLinecap="round" />
              </svg>
              <input
                type="text"
                placeholder="Search jobs..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleSearch();
                }}
                disabled={forYou}
                aria-label="Search jobs"
                className="w-full rounded-xl border border-slate-300 bg-white py-3 pl-11 pr-4 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 hover:border-slate-400 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 disabled:bg-slate-100"
              />
            </div>
            <div>
              <input
                type="text"
                placeholder="Location"
                value={locationFilter}
                onChange={(e) => setLocationFilter(e.target.value)}
                disabled={forYou}
                aria-label="Filter by location"
                className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 hover:border-slate-400 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 disabled:bg-slate-100"
              />
            </div>
            <div>
              <select
                value={jobTypeFilter}
                onChange={(e) => setJobTypeFilter(e.target.value)}
                disabled={forYou}
                aria-label="Filter by job type"
                className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-700 outline-none transition hover:border-slate-400 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 disabled:bg-slate-100"
              >
                <option value="">All Job Types</option>
                <option value="full-time">Full-time</option>
                <option value="part-time">Part-time</option>
                <option value="contract">Contract</option>
                <option value="remote">Remote</option>
              </select>
            </div>
            <div>
              <select
                value={fieldFilter}
                onChange={(e) => {
                  setFieldFilter(e.target.value);
                }}
                disabled={forYou}
                aria-label="Filter by field"
                className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-700 outline-none transition hover:border-slate-400 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 disabled:bg-slate-100"
              >
                <option value="">All Fields</option>
                {Object.entries(FIELD_LABELS).map(([value, label]) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </select>
            </div>
            <div className="flex gap-2 md:col-span-2 xl:col-span-1">
              <button
                onClick={handleSearch}
                disabled={forYou}
                className="flex-1 rounded-xl bg-indigo-600 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700 focus:outline-none focus:ring-4 focus:ring-indigo-500/20 disabled:cursor-not-allowed disabled:bg-slate-300"
              >
                Search
              </button>
              <button
                onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
                disabled={forYou}
                aria-expanded={showAdvancedFilters}
                aria-label={showAdvancedFilters ? 'Hide advanced filters' : 'Show advanced filters'}
                className="inline-flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 focus:outline-none focus:ring-4 focus:ring-indigo-500/10 disabled:cursor-not-allowed disabled:bg-slate-100"
              >
                <svg viewBox="0 0 20 20" fill="none" className={`h-4 w-4 transition-transform ${showAdvancedFilters ? 'rotate-180' : ''}`} stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
                  <path d="m5 7.5 5 5 5-5" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </button>
            </div>
          </div>

          {/* Advanced Filters */}
          {showAdvancedFilters && (
            <div className="mt-5 border-t border-slate-100 pt-5">
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                {/* Remote Toggle */}
                <div className="flex items-center gap-3 rounded-xl border border-slate-200 px-3 py-2.5">
                  <input
                    type="checkbox"
                    id="remote-only"
                    checked={remoteOnly}
                    onChange={(e) => setRemoteOnly(e.target.checked)}
                    disabled={forYou}
                    className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 disabled:bg-slate-100"
                  />
                  <label htmlFor="remote-only" className="text-sm font-medium text-slate-700">
                    Remote Only
                  </label>
                </div>

                {/* Salary Range */}
                <div className="flex gap-2">
                  <div className="flex-1">
                    <input
                      type="number"
                      placeholder="Min Salary (ETB)"
                      value={salaryMin}
                      onChange={(e) => setSalaryMin(e.target.value)}
                      disabled={forYou}
                      className="w-full rounded-xl border border-slate-300 px-3 py-2.5 text-sm outline-none transition placeholder:text-slate-400 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 disabled:bg-slate-100"
                    />
                  </div>
                  <div className="flex-1">
                    <input
                      type="number"
                      placeholder="Max Salary (ETB)"
                      value={salaryMax}
                      onChange={(e) => setSalaryMax(e.target.value)}
                      disabled={forYou}
                      className="w-full rounded-xl border border-slate-300 px-3 py-2.5 text-sm outline-none transition placeholder:text-slate-400 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 disabled:bg-slate-100"
                    />
                  </div>
                </div>

                {/* Deadline Filter */}
                <div>
                  <select
                    value={deadlineDays}
                    onChange={(e) => setDeadlineDays(e.target.value)}
                    disabled={forYou}
                    className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-700 outline-none transition focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 disabled:bg-slate-100"
                  >
                    <option value="">Any Deadline</option>
                    <option value="1">Closing within 1 day</option>
                    <option value="3">Closing within 3 days</option>
                    <option value="7">Closing within 1 week</option>
                    <option value="14">Closing within 2 weeks</option>
                    <option value="30">Closing within 1 month</option>
                  </select>
                </div>

                {/* Clear Filters */}
                <button
                  onClick={clearFilters}
                  disabled={forYou || getActiveFiltersCount() === 0}
                  className="rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-600 transition hover:border-red-200 hover:bg-red-50 hover:text-red-700 disabled:cursor-not-allowed disabled:bg-slate-50 disabled:text-slate-400"
                >
                  Clear All Filters
                </button>
              </div>

              {/* Active Filters Display */}
              {getActiveFiltersCount() > 0 && (
                <div className="mt-4 flex flex-wrap gap-2">
                  {appliedSearchTerm && (
                    <span className="inline-flex items-center gap-2 rounded-full border border-indigo-100 bg-indigo-50 px-3 py-1 text-sm text-indigo-800">
                      Search: {appliedSearchTerm}
                      <button
                        onClick={() => {
                          setSearchTerm('');
                          setAppliedSearchTerm('');
                        }}
                        aria-label="Remove search filter"
                        className="font-semibold hover:text-indigo-600"
                      >×</button>
                    </span>
                  )}
                  {locationFilter && (
                    <span className="inline-flex items-center gap-2 rounded-full border border-indigo-100 bg-indigo-50 px-3 py-1 text-sm text-indigo-800">
                      Location: {locationFilter}
                      <button onClick={() => setLocationFilter('')} aria-label="Remove location filter" className="font-semibold hover:text-indigo-600">×</button>
                    </span>
                  )}
                  {jobTypeFilter && (
                    <span className="inline-flex items-center gap-2 rounded-full border border-indigo-100 bg-indigo-50 px-3 py-1 text-sm text-indigo-800">
                      Type: {jobTypeFilter}
                      <button onClick={() => setJobTypeFilter('')} aria-label="Remove job type filter" className="font-semibold hover:text-indigo-600">×</button>
                    </span>
                  )}
                  {fieldFilter && FIELD_LABELS[fieldFilter] && (
                    <span className="inline-flex items-center gap-2 rounded-full border border-indigo-100 bg-indigo-50 px-3 py-1 text-sm text-indigo-800">
                      Field: {FIELD_LABELS[fieldFilter]}
                      <button onClick={() => setFieldFilter('')} aria-label="Remove field filter" className="font-semibold hover:text-indigo-600">×</button>
                    </span>
                  )}
                  {remoteOnly && (
                    <span className="inline-flex items-center gap-2 rounded-full border border-emerald-100 bg-emerald-50 px-3 py-1 text-sm text-emerald-800">
                      Remote Only
                      <button onClick={() => setRemoteOnly(false)} aria-label="Remove remote-only filter" className="font-semibold hover:text-emerald-600">×</button>
                    </span>
                  )}
                  {salaryMin && (
                    <span className="inline-flex items-center gap-2 rounded-full border border-indigo-100 bg-indigo-50 px-3 py-1 text-sm text-indigo-800">
                      Min: {formatSalary(parseInt(salaryMin))}
                      <button onClick={() => setSalaryMin('')} aria-label="Remove minimum salary filter" className="font-semibold hover:text-indigo-600">×</button>
                    </span>
                  )}
                  {salaryMax && (
                    <span className="inline-flex items-center gap-2 rounded-full border border-indigo-100 bg-indigo-50 px-3 py-1 text-sm text-indigo-800">
                      Max: {formatSalary(parseInt(salaryMax))}
                      <button onClick={() => setSalaryMax('')} aria-label="Remove maximum salary filter" className="font-semibold hover:text-indigo-600">×</button>
                    </span>
                  )}
                  {deadlineDays && (
                    <span className="inline-flex items-center gap-2 rounded-full border border-indigo-100 bg-indigo-50 px-3 py-1 text-sm text-indigo-800">
                      Deadline: ≤{deadlineDays} days
                      <button onClick={() => setDeadlineDays('')} aria-label="Remove deadline filter" className="font-semibold hover:text-indigo-600">×</button>
                    </span>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Results Info */}
        {!loading && (
          <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
            <p className="text-sm text-slate-600">
              <span className="font-semibold text-slate-900">{jobs.length}</span> job{jobs.length !== 1 ? 's' : ''} found
              {getActiveFiltersCount() > 0 && ` · ${getActiveFiltersCount()} active filter${getActiveFiltersCount() !== 1 ? 's' : ''}`}
            </p>
            {forYou && (
              <span className="inline-flex items-center gap-1.5 rounded-full border border-indigo-100 bg-indigo-50 px-3 py-1 text-xs font-semibold text-indigo-700">
                <svg viewBox="0 0 24 24" fill="none" className="h-3.5 w-3.5" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
                  <path d="M12 3.5 14.6 9l5.9.8-4.3 4.1 1 5.8-5.2-2.8-5.2 2.8 1-5.8-4.3-4.1 5.9-.8L12 3.5Z" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                Personalized for you
              </span>
            )}
          </div>
        )}

        {/* Jobs List */}
        {loading ? (
          <div role="status" className="rounded-2xl border border-slate-200 bg-white px-6 py-16 text-center shadow-sm">
            <span className="mx-auto flex h-11 w-11 items-center justify-center rounded-full bg-indigo-50">
              <span className="h-5 w-5 animate-spin rounded-full border-2 border-indigo-200 border-t-indigo-600" />
            </span>
            <p className="mt-4 font-semibold text-slate-900">Finding opportunities</p>
            <p className="mt-1 text-sm text-slate-500">This should only take a moment.</p>
          </div>
        ) : searchError ? (
          <div role="alert" className="rounded-2xl border border-red-200 bg-red-50 p-5 text-sm leading-6 text-red-800">
            <p className="font-semibold">We couldn’t load the jobs</p>
            <p className="mt-1">{searchError}</p>
            <button onClick={() => setRefreshKey((key) => key + 1)} className="mt-3 rounded-lg bg-white px-3 py-2 font-semibold text-red-800 shadow-sm ring-1 ring-red-200 transition hover:bg-red-100">
              Try again
            </button>
          </div>
        ) : jobs.length === 0 ? (
          <div className="rounded-2xl border border-slate-200 bg-white px-6 py-14 text-center shadow-sm">
            <span className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-100 text-slate-500">
              <svg viewBox="0 0 24 24" fill="none" className="h-7 w-7" stroke="currentColor" strokeWidth="1.7" aria-hidden="true">
                <circle cx="10.8" cy="10.8" r="6.8" />
                <path d="m16 16 4 4M8 10.8h5.6" strokeLinecap="round" />
              </svg>
            </span>
            <h2 className="mt-4 text-lg font-semibold text-slate-900">No jobs found</h2>
            <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500">Try adjusting your search or removing a filter to see more opportunities.</p>
            {getActiveFiltersCount() > 0 && (
              <button
                onClick={clearFilters}
                className="mt-5 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-indigo-700"
              >
                Clear filters and try again
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            {jobs.map((job) => (
              <article key={job.external_id} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:border-indigo-200 hover:shadow-lg hover:shadow-slate-200/60 sm:p-6">
                <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <h2 className="text-lg font-semibold tracking-tight text-slate-950 sm:text-xl">{job.title}</h2>
                      {job.field && job.field !== 'other' && FIELD_LABELS[job.field] && (
                        <span className="rounded-full border border-indigo-100 bg-indigo-50 px-2.5 py-1 text-xs font-semibold text-indigo-700">
                          {FIELD_LABELS[job.field]}
                        </span>
                      )}
                    </div>
                    <p className="mt-1.5 font-medium text-slate-700">{job.company}</p>
                    <div className="mt-4 flex flex-wrap gap-x-4 gap-y-2 text-sm text-slate-600">
                      {job.location && (
                        <span className="flex items-center gap-1.5">
                          <svg viewBox="0 0 20 20" fill="none" className="h-4 w-4 text-slate-400" stroke="currentColor" strokeWidth="1.6" aria-hidden="true">
                            <path d="M16 8.3c0 4.2-6 9-6 9s-6-4.8-6-9a6 6 0 1 1 12 0Z" />
                            <circle cx="10" cy="8" r="2" />
                          </svg>
                          {job.location}
                        </span>
                      )}
                      {job.job_type && (
                        <span className="flex items-center gap-1.5 capitalize">
                          <svg viewBox="0 0 20 20" fill="none" className="h-4 w-4 text-slate-400" stroke="currentColor" strokeWidth="1.6" aria-hidden="true">
                            <rect x="2.5" y="6" width="15" height="11" rx="2" />
                            <path d="M7 6V4.5A1.5 1.5 0 0 1 8.5 3h3A1.5 1.5 0 0 1 13 4.5V6M2.5 10.5h15m-9 0V12h3v-1.5" strokeLinecap="round" strokeLinejoin="round" />
                          </svg>
                          {job.job_type}
                        </span>
                      )}
                      {job.salary_min && job.salary_max && (
                        <span className="flex items-center gap-1.5">
                          <svg viewBox="0 0 20 20" fill="none" className="h-4 w-4 text-slate-400" stroke="currentColor" strokeWidth="1.6" aria-hidden="true">
                            <circle cx="10" cy="10" r="7.5" />
                            <path d="M12.5 7.5c-.5-.6-1.3-.9-2.4-.9-1.2 0-2 .6-2 1.5 0 2.3 4.8.8 4.8 3.3 0 1-.9 1.8-2.4 1.8-1.1 0-2.1-.4-2.7-1.1M10 5.2v1.4m0 6.7v1.5" strokeLinecap="round" />
                          </svg>
                          {formatSalary(job.salary_min)} - {formatSalary(job.salary_max)}
                        </span>
                      )}
                      {job.deadline && (
                        <span className={`flex items-center gap-1.5 ${getDeadlineDisplay(job.deadline).urgent ? 'font-semibold text-rose-700' : 'text-slate-600'}`}>
                          <svg viewBox="0 0 20 20" fill="none" className={`h-4 w-4 ${getDeadlineDisplay(job.deadline).urgent ? 'text-rose-500' : 'text-slate-400'}`} stroke="currentColor" strokeWidth="1.6" aria-hidden="true">
                            <circle cx="10" cy="10" r="7.5" />
                            <path d="M10 5.5v4.8l3 1.8" strokeLinecap="round" strokeLinejoin="round" />
                          </svg>
                          {getDeadlineDisplay(job.deadline).text}
                        </span>
                      )}
                    </div>
                    <p className="mt-4 line-clamp-2 text-sm leading-6 text-slate-600">
                      {job.description}
                    </p>
                    {job.skills && (
                      <div className="mt-4 flex flex-wrap gap-2">
                        {JSON.parse(job.skills).slice(0, 5).map((skill: string, index: number) => (
                          <span
                            key={index}
                            className="rounded-lg bg-slate-100 px-2.5 py-1.5 text-xs font-medium text-slate-700"
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <a
                    href={job.apply_url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl bg-indigo-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-indigo-700 focus:outline-none focus:ring-4 focus:ring-indigo-500/20 sm:ml-4"
                  >
                    Apply
                    <svg viewBox="0 0 20 20" fill="none" className="h-4 w-4" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
                      <path d="M7 4h9v9m0-9-9 9m-2-5v8h8" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </a>
                </div>
              </article>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
