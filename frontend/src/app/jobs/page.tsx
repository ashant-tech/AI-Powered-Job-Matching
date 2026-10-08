'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { jobApi, FIELD_LABELS, ETHIOPIAN_CITIES } from '../../services/jobApi';

export default function JobsPage() {
  const router = useRouter();
  const [jobs, setJobs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [appliedSearchTerm, setAppliedSearchTerm] = useState('');
  const [searchError, setSearchError] = useState('');
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
      <main className="container mx-auto px-4 py-8">
        {/* Search and Filters */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          {token && (
            <div className="mb-4">
              <button
                onClick={() => setForYou(!forYou)}
                className={`px-4 py-2 rounded-lg font-semibold transition ${
                  forYou
                    ? 'bg-indigo-600 text-white'
                    : 'bg-indigo-100 text-indigo-700 hover:bg-indigo-200'
                }`}
              >
                ✨ For You (by your department & skills)
              </button>
            </div>
          )}

          {/* Basic Filters */}
          <div className="grid md:grid-cols-5 gap-4 mb-4">
            <div>
              <input
                type="text"
                placeholder="Search jobs..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleSearch();
                }}
                disabled={forYou}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-gray-100"
              />
            </div>
            <div>
              <input
                type="text"
                placeholder="Location"
                value={locationFilter}
                onChange={(e) => setLocationFilter(e.target.value)}
                disabled={forYou}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-gray-100"
              />
            </div>
            <div>
              <select
                value={jobTypeFilter}
                onChange={(e) => setJobTypeFilter(e.target.value)}
                disabled={forYou}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-gray-100"
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
                  console.log('Field filter changed to:', e.target.value);
                  setFieldFilter(e.target.value);
                }}
                disabled={forYou}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-gray-100"
              >
                <option value="">All Fields</option>
                {Object.entries(FIELD_LABELS).map(([value, label]) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </select>
            </div>
            <div className="flex gap-2">
              <button
                onClick={handleSearch}
                disabled={forYou}
                className="flex-1 bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 transition disabled:bg-gray-300"
              >
                Search
              </button>
              <button
                onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
                disabled={forYou}
                className="px-4 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition disabled:bg-gray-100"
              >
                {showAdvancedFilters ? '▼' : '▶'}
              </button>
            </div>
          </div>

          {/* Advanced Filters */}
          {showAdvancedFilters && (
            <div className="border-t pt-4 mt-4">
              <div className="grid md:grid-cols-4 gap-4">
                {/* Remote Toggle */}
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="remote-only"
                    checked={remoteOnly}
                    onChange={(e) => setRemoteOnly(e.target.checked)}
                    disabled={forYou}
                    className="w-5 h-5 text-indigo-600 rounded focus:ring-indigo-500 disabled:bg-gray-100"
                  />
                  <label htmlFor="remote-only" className="text-sm font-medium text-gray-700 disabled:text-gray-400">
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
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-gray-100 text-sm"
                    />
                  </div>
                  <div className="flex-1">
                    <input
                      type="number"
                      placeholder="Max Salary (ETB)"
                      value={salaryMax}
                      onChange={(e) => setSalaryMax(e.target.value)}
                      disabled={forYou}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-gray-100 text-sm"
                    />
                  </div>
                </div>

                {/* Deadline Filter */}
                <div>
                  <select
                    value={deadlineDays}
                    onChange={(e) => setDeadlineDays(e.target.value)}
                    disabled={forYou}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent disabled:bg-gray-100 text-sm"
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
                  className="bg-red-100 text-red-700 px-4 py-2 rounded-lg hover:bg-red-200 transition disabled:bg-gray-100 disabled:text-gray-400 text-sm font-semibold"
                >
                  Clear All Filters
                </button>
              </div>

              {/* Active Filters Display */}
              {getActiveFiltersCount() > 0 && (
                <div className="mt-4 flex flex-wrap gap-2">
                  {appliedSearchTerm && (
                    <span className="bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full text-sm flex items-center gap-2">
                      Search: {appliedSearchTerm}
                      <button
                        onClick={() => {
                          setSearchTerm('');
                          setAppliedSearchTerm('');
                        }}
                        className="hover:text-indigo-600"
                      >×</button>
                    </span>
                  )}
                  {locationFilter && (
                    <span className="bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full text-sm flex items-center gap-2">
                      Location: {locationFilter}
                      <button onClick={() => setLocationFilter('')} className="hover:text-indigo-600">×</button>
                    </span>
                  )}
                  {jobTypeFilter && (
                    <span className="bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full text-sm flex items-center gap-2">
                      Type: {jobTypeFilter}
                      <button onClick={() => setJobTypeFilter('')} className="hover:text-indigo-600">×</button>
                    </span>
                  )}
                  {fieldFilter && FIELD_LABELS[fieldFilter] && (
                    <span className="bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full text-sm flex items-center gap-2">
                      Field: {FIELD_LABELS[fieldFilter]}
                      <button onClick={() => setFieldFilter('')} className="hover:text-indigo-600">×</button>
                    </span>
                  )}
                  {remoteOnly && (
                    <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm flex items-center gap-2">
                      Remote Only
                      <button onClick={() => setRemoteOnly(false)} className="hover:text-green-600">×</button>
                    </span>
                  )}
                  {salaryMin && (
                    <span className="bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full text-sm flex items-center gap-2">
                      Min: {formatSalary(parseInt(salaryMin))}
                      <button onClick={() => setSalaryMin('')} className="hover:text-indigo-600">×</button>
                    </span>
                  )}
                  {salaryMax && (
                    <span className="bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full text-sm flex items-center gap-2">
                      Max: {formatSalary(parseInt(salaryMax))}
                      <button onClick={() => setSalaryMax('')} className="hover:text-indigo-600">×</button>
                    </span>
                  )}
                  {deadlineDays && (
                    <span className="bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full text-sm flex items-center gap-2">
                      Deadline: ≤{deadlineDays} days
                      <button onClick={() => setDeadlineDays('')} className="hover:text-indigo-600">×</button>
                    </span>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Results Info */}
        {!loading && (
          <div className="mb-4 text-sm text-gray-600">
            {jobs.length} job{jobs.length !== 1 ? 's' : ''} found
            {getActiveFiltersCount() > 0 && ` with ${getActiveFiltersCount()} active filter${getActiveFiltersCount() !== 1 ? 's' : ''}`}
          </div>
        )}

        {/* Jobs List */}
        {loading ? (
          <div className="text-center py-8">
            <div className="text-xl">Loading jobs...</div>
          </div>
        ) : searchError ? (
          <div role="alert" className="bg-red-50 text-red-700 rounded-lg p-4">
            {searchError}
          </div>
        ) : jobs.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <div className="text-gray-600 mb-4">No jobs found matching your criteria</div>
            {getActiveFiltersCount() > 0 && (
              <button
                onClick={clearFilters}
                className="text-indigo-600 hover:underline"
              >
                Clear filters and try again
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            {jobs.map((job) => (
              <div key={job.external_id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-gray-900 mb-2">{job.title}</h3>
                    <p className="text-indigo-600 font-semibold mb-2">{job.company}</p>
                    <div className="flex gap-4 text-sm text-gray-600 mb-3">
                      {job.field && job.field !== 'other' && FIELD_LABELS[job.field] && (
                        <span className="bg-purple-100 text-purple-800 px-2 py-0.5 rounded-full text-xs font-semibold">
                          {FIELD_LABELS[job.field]}
                        </span>
                      )}
                      {job.location && (
                        <span className="flex items-center gap-1">
                          📍 {job.location}
                        </span>
                      )}
                      {job.job_type && (
                        <span className="flex items-center gap-1">
                          💼 {job.job_type}
                        </span>
                      )}
                      {job.salary_min && job.salary_max && (
                        <span className="flex items-center gap-1">
                          💰 {formatSalary(job.salary_min)} - {formatSalary(job.salary_max)}
                        </span>
                      )}
                      {job.deadline && (
                        <span className={`flex items-center gap-1 ${getDeadlineDisplay(job.deadline).urgent ? 'text-red-600 font-semibold' : ''}`}>
                          ⏳ {getDeadlineDisplay(job.deadline).text}
                        </span>
                      )}
                    </div>
                    <p className="text-gray-600 line-clamp-2 mb-3">
                      {job.description}
                    </p>
                    {job.skills && (
                      <div className="flex flex-wrap gap-2">
                        {JSON.parse(job.skills).slice(0, 5).map((skill: string, index: number) => (
                          <span
                            key={index}
                            className="bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full text-sm"
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
                    className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition ml-4"
                  >
                    Apply
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
