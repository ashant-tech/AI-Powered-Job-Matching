'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [stats, setStats] = useState({
    totalMatches: 0,
    pendingApplications: 0,
    viewedJobs: 0,
    unreadNotifications: 0,
  });
  const [recentActivity, setRecentActivity] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  // An expired/invalid token must send the user back to login instead of
  // silently rendering an empty dashboard with zeroed stats.
  const authedFetch = async (path: string) => {
    const token = localStorage.getItem('token');
    const response = await fetch(path, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    if (response.status === 401) {
      localStorage.removeItem('token');
      router.push('/login');
      return null;
    }
    return response;
  };

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    fetchUserData();
    fetchStats();
    fetchRecentActivity();

    const statsInterval = window.setInterval(() => {
      if (document.visibilityState === 'visible') {
        fetchStats();
        fetchRecentActivity();
      }
    }, 5000);
    const refreshDashboardOnFocus = () => {
      fetchStats();
      fetchRecentActivity();
    };
    window.addEventListener('focus', refreshDashboardOnFocus);

    return () => {
      window.clearInterval(statsInterval);
      window.removeEventListener('focus', refreshDashboardOnFocus);
    };
  }, [router]);

  const fetchUserData = async () => {
    try {
      const response = await authedFetch('/api/auth/me');
      if (response && response.ok) {
        const userData = await response.json();
        setUser(userData);
      }
    } catch (error) {
      console.error('Error fetching user data:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await authedFetch('/api/matching/stats');
      if (response && response.ok) {
        const statsData = await response.json();
        setStats(statsData);
        setLastUpdated(new Date());
      } else if (response) {
        console.error('Failed to fetch stats');
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchRecentActivity = async () => {
    try {
      const response = await authedFetch('/api/matching/recent-activity');
      if (response && response.ok) {
        const activityData = await response.json();
        setRecentActivity(activityData);
      }
    } catch (error) {
      console.error('Error fetching recent activity:', error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    router.push('/login');
  };

  if (loading) {
    return (
      <div role="status" className="flex min-h-screen items-center justify-center bg-slate-50">
        <div className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-white px-5 py-4 text-sm font-medium text-slate-600 shadow-sm">
          <span className="h-5 w-5 animate-spin rounded-full border-2 border-indigo-200 border-t-indigo-600" />
          Loading your dashboard...
        </div>
      </div>
    );
  }

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
          <nav aria-label="Dashboard navigation" className="flex items-center gap-2 sm:gap-3">
            <Link href="/jobs" className="hidden rounded-lg px-3 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100 hover:text-slate-900 sm:inline-flex">Browse jobs</Link>
            <Link href="/profile" aria-label="Profile" className="flex h-10 w-10 items-center justify-center rounded-full bg-indigo-50 text-sm font-bold text-indigo-700 ring-1 ring-indigo-100 transition hover:bg-indigo-100">
              {(user?.full_name || user?.username || 'U').slice(0, 1).toUpperCase()}
            </Link>
            <button
              onClick={handleLogout}
              className="rounded-lg border border-slate-200 px-3 py-2 text-sm font-semibold text-slate-600 transition hover:border-red-200 hover:bg-red-50 hover:text-red-700"
            >
              Sign out
            </button>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-7 sm:px-6 sm:py-10 lg:px-8">
        <section className="relative mb-7 overflow-hidden rounded-3xl bg-gradient-to-br from-slate-950 via-indigo-950 to-indigo-800 px-6 py-8 text-white shadow-lg shadow-indigo-950/10 sm:px-8 sm:py-10">
          <div aria-hidden="true" className="absolute -right-16 -top-28 h-72 w-72 rounded-full border-[32px] border-white/[0.06]" />
          <div className="relative flex flex-col gap-7 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="text-sm font-semibold text-indigo-200">Your career workspace</p>
              <h1 className="mt-2 text-3xl font-semibold tracking-tight sm:text-4xl">
                Welcome{user?.full_name || user?.username ? `, ${user.full_name || user.username}` : ' back'}
              </h1>
              <p className="mt-3 max-w-xl text-sm leading-6 text-indigo-100/80 sm:text-base">
                Keep track of your matches, explore new roles, and take your next career step.
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <Link href="/recommendations" className="inline-flex items-center justify-center gap-2 rounded-xl bg-white px-4 py-3 text-sm font-semibold text-indigo-900 transition hover:bg-indigo-50">
                View my matches
                <svg viewBox="0 0 20 20" fill="none" className="h-4 w-4" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
                  <path d="M4 10h12m-5-5 5 5-5 5" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </Link>
              <Link href="/jobs" className="inline-flex items-center justify-center rounded-xl border border-white/20 bg-white/[0.08] px-4 py-3 text-sm font-semibold text-white transition hover:bg-white/[0.14]">
                Browse jobs
              </Link>
            </div>
          </div>
        </section>

        {/* Stats Cards */}
        <div className="mb-9">
          <div className="mb-4 flex flex-wrap items-end justify-between gap-2">
            <div>
              <h2 className="text-lg font-semibold text-slate-900">Your activity</h2>
              <p className="mt-1 text-sm text-slate-500">A quick overview of your job search.</p>
            </div>
            <div className="flex items-center gap-2 text-xs text-slate-500">
              <span className="relative flex h-2.5 w-2.5">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-40" />
                <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-emerald-500" />
              </span>
              Updated{lastUpdated ? ` ${lastUpdated.toLocaleTimeString()}` : ' just now'}
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
            {[
              { label: 'Job matches', value: stats.totalMatches, tone: 'indigo', icon: 'M12 3.5 14.6 9l5.9.8-4.3 4.1 1 5.8-5.2-2.8-5.2 2.8 1-5.8-4.3-4.1 5.9-.8L12 3.5Z' },
              { label: 'To review', value: stats.pendingApplications, tone: 'amber', icon: 'M7 3.5h7l4 4V20a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4.5a1 1 0 0 1 1-1Z' },
              { label: 'Viewed jobs', value: stats.viewedJobs, tone: 'sky', icon: 'M2.5 10s2.7-5 7.5-5 7.5 5 7.5 5-2.7 5-7.5 5-7.5-5-7.5-5Z' },
              { label: 'Notifications', value: stats.unreadNotifications, tone: 'rose', icon: 'M15 17h5l-1.4-1.4a2 2 0 0 1-.6-1.4V11a6 6 0 0 0-5-5.9V4a1 1 0 0 0-2 0v1.1A6 6 0 0 0 6 11v3.2a2 2 0 0 1-.6 1.4L4 17h5m2 0v1a2 2 0 0 0 4 0v-1' },
            ].map((stat) => (
              <div key={stat.label} className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <p className="text-sm font-medium text-slate-500">{stat.label}</p>
                    <p className="mt-3 text-3xl font-semibold tracking-tight text-slate-950">{stat.value}</p>
                  </div>
                  <span className={`flex h-10 w-10 items-center justify-center rounded-xl ${
                    stat.tone === 'indigo' ? 'bg-indigo-50 text-indigo-600' :
                    stat.tone === 'amber' ? 'bg-amber-50 text-amber-600' :
                    stat.tone === 'sky' ? 'bg-sky-50 text-sky-600' :
                    'bg-rose-50 text-rose-600'
                  }`}>
                    <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" stroke="currentColor" strokeWidth="1.7" aria-hidden="true">
                      <path d={stat.icon} strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <section className="mb-9">
          <div className="mb-4">
            <h2 className="text-lg font-semibold text-slate-900">Your job search</h2>
            <p className="mt-1 text-sm text-slate-500">The tools you need to move forward.</p>
          </div>
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {[
              { href: '/upload-cv', title: 'Upload your CV', desc: 'Add or update your experience', tone: 'indigo', icon: 'M7 3.5h7l4 4V20a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4.5a1 1 0 0 1 1-1Z M14 4v4h4M9 13h6M9 16h4' },
              { href: '/recommendations', title: 'Review job matches', desc: 'See roles selected for your profile', tone: 'emerald', icon: 'M12 3.5 14.6 9l5.9.8-4.3 4.1 1 5.8-5.2-2.8-5.2 2.8 1-5.8-4.3-4.1 5.9-.8L12 3.5Z' },
              { href: '/jobs', title: 'Browse all jobs', desc: 'Search every available listing', tone: 'sky', icon: 'M10.8 17.6a6.8 6.8 0 1 0 0-13.6 6.8 6.8 0 0 0 0 13.6ZM16 16l4 4' },
              { href: '/career-guidance', title: 'Career guidance', desc: 'Explore your next career step', tone: 'violet', icon: 'M12 3v3m0 12v3m9-9h-3M6 12H3m15.4-6.4-2.1 2.1M7.7 16.3l-2.1 2.1m12.8 0-2.1-2.1M7.7 7.7 5.6 5.6M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z' },
              { href: '/resume-analysis', title: 'Improve your resume', desc: 'Get feedback on your CV', tone: 'amber', icon: 'M7 3.5h7l4 4V20a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4.5a1 1 0 0 1 1-1Z M14 4v4h4M9 13h6M9 16h6' },
              { href: '/notifications', title: 'Notifications', desc: 'Check important updates', tone: 'rose', icon: 'M15 17h5l-1.4-1.4a2 2 0 0 1-.6-1.4V11a6 6 0 0 0-5-5.9V4a1 1 0 0 0-2 0v1.1A6 6 0 0 0 6 11v3.2a2 2 0 0 1-.6 1.4L4 17h5m2 0v1a2 2 0 0 0 4 0v-1' },
            ].map((action) => (
              <Link key={action.href} href={action.href} className="group flex items-center gap-4 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:border-indigo-200 hover:shadow-md sm:p-5">
                <span className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-xl ${
                  action.tone === 'indigo' ? 'bg-indigo-50 text-indigo-600' :
                  action.tone === 'emerald' ? 'bg-emerald-50 text-emerald-600' :
                  action.tone === 'sky' ? 'bg-sky-50 text-sky-600' :
                  action.tone === 'violet' ? 'bg-violet-50 text-violet-600' :
                  action.tone === 'amber' ? 'bg-amber-50 text-amber-600' :
                  'bg-rose-50 text-rose-600'
                }`}>
                  <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" stroke="currentColor" strokeWidth="1.7" aria-hidden="true">
                    <path d={action.icon} strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </span>
                <span className="min-w-0 flex-1">
                  <span className="block font-semibold text-slate-900">{action.title}</span>
                  <span className="mt-1 block text-sm text-slate-500">{action.desc}</span>
                </span>
                <svg viewBox="0 0 20 20" fill="none" className="h-4 w-4 shrink-0 text-slate-400 transition group-hover:translate-x-0.5 group-hover:text-indigo-600" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
                  <path d="m7 4 6 6-6 6" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </Link>
            ))}
          </div>
        </section>

        {/* AI-Powered Features */}
        <section className="mb-9 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
          <div className="mb-5">
            <p className="text-sm font-semibold text-indigo-600">More ways to grow</p>
            <h2 className="mt-1 text-lg font-semibold text-slate-900">Career tools</h2>
            <p className="mt-1 text-sm text-slate-500">Explore additional resources for your next move.</p>
          </div>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {[
              { href: '/interview-prep', title: 'Interview preparation', desc: 'Practice common interview questions' },
              { href: '/career-transition', title: 'Career transition', desc: 'Explore a change in direction' },
              { href: '/learning-hub', title: 'Learning hub', desc: 'Plan skills you want to develop' },
              { href: '/salary-negotiation', title: 'Salary negotiation', desc: 'Prepare for compensation talks' },
              { href: '/network-analysis', title: 'Network insights', desc: 'Build your professional network' },
              { href: '/culture-match', title: 'Workplace preferences', desc: 'Reflect on your ideal work culture' },
            ].map((tool) => (
              <Link key={tool.href} href={tool.href} className="rounded-xl border border-slate-100 bg-slate-50/70 p-4 transition hover:border-indigo-200 hover:bg-indigo-50/50">
                <span className="font-semibold text-slate-800">{tool.title}</span>
                <span className="mt-1 block text-sm leading-5 text-slate-500">{tool.desc}</span>
              </Link>
            ))}
          </div>
        </section>

        {/* Recent Activity */}
        <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
          <div className="flex items-end justify-between gap-3">
            <div>
              <h2 className="text-lg font-semibold text-slate-900">Recent activity</h2>
              <p className="mt-1 text-sm text-slate-500">Updates from your job search.</p>
            </div>
            <Link href="/notifications" className="text-sm font-semibold text-indigo-700 transition hover:text-indigo-900">View notifications</Link>
          </div>
          <div className="mt-5 divide-y divide-slate-100">
            {recentActivity.length > 0 ? (
              recentActivity.map((activity, index) => (
                <div key={index} className="flex items-start gap-4 py-4 first:pt-0 last:pb-0">
                  <span className={`mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${
                    activity.type === 'notification' ? 'bg-amber-50 text-amber-600' : 'bg-emerald-50 text-emerald-600'
                  }`}>
                    {activity.type === 'notification' ? (
                      <svg viewBox="0 0 20 20" fill="none" className="h-5 w-5" stroke="currentColor" strokeWidth="1.7" aria-hidden="true">
                        <path d="M15 14h3l-1-1a1.5 1.5 0 0 1-.5-1.1V9.5a4.5 4.5 0 0 0-9 0v2.4A1.5 1.5 0 0 1 7 13l-1 1h3m2 0v.5a1.5 1.5 0 0 0 3 0V14" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                    ) : (
                      <svg viewBox="0 0 20 20" fill="none" className="h-5 w-5" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
                        <path d="m4 10 4 4 8-8" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                    )}
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="font-semibold text-slate-900">{activity.title}</p>
                    <p className="mt-1 text-sm text-slate-600">{activity.message || activity.company}</p>
                    <p className="mt-1 text-xs text-slate-400">{new Date(activity.time).toLocaleString()}</p>
                  </div>
                </div>
              ))
            ) : (
              <div className="rounded-xl bg-slate-50 px-4 py-8 text-center">
                <p className="font-medium text-slate-700">No recent activity yet</p>
                <p className="mt-1 text-sm text-slate-500">Your matches and updates will appear here.</p>
                <Link href="/jobs" className="mt-4 inline-flex text-sm font-semibold text-indigo-700 hover:text-indigo-900">Browse jobs</Link>
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}
