'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('reset') === 'success') {
      setNotice('Your password has been reset. You can now sign in.');
    }
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // 502/503/504 usually mean the backend free instance is cold-starting;
      // retry once after a short pause instead of showing a hard error.
      const COLD_START = new Set([502, 503, 504]);
      let response: Response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          username: formData.email,
          password: formData.password,
        }),
      });
      if (COLD_START.has(response.status)) {
        setError('Server is starting up, retrying…');
        await new Promise((r) => setTimeout(r, 3000));
        response = await fetch('/api/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: new URLSearchParams({
            username: formData.email,
            password: formData.password,
          }),
        });
        setError('');
      }

      const responseBody = await response.text();
      let data: Record<string, unknown> = {};
      try {
        const parsedBody: unknown = JSON.parse(responseBody);
        if (typeof parsedBody === 'object' && parsedBody !== null) {
          data = parsedBody as Record<string, unknown>;
        }
      } catch {
        // Non-JSON body (gateway/proxy error page) — mapped to a clear message below.
      }

      if (!response.ok) {
        let message: string;
        if (response.status === 401) {
          message = 'Invalid email or password';
        } else if (response.status === 429) {
          const retryAfter = Number(response.headers.get('Retry-After'));
          message = Number.isFinite(retryAfter) && retryAfter > 0
            ? `Too many login attempts. Please try again in ${retryAfter} seconds.`
            : 'Too many login attempts. Please wait a minute and try again.';
        } else if (COLD_START.has(response.status)) {
          message = 'The server is still starting up. Please wait a few seconds and try again.';
        } else if (typeof data.detail === 'string') {
          message = data.detail;
        } else {
          message = 'Login service is unavailable right now. Please try again in a moment.';
        }
        throw new Error(message);
      }

      if (typeof data.access_token !== 'string') {
        throw new Error('Login response did not include an access token');
      }

      localStorage.setItem('token', data.access_token);
      router.push('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-6 sm:px-6 lg:flex lg:items-center lg:justify-center lg:py-12">
      <div className="mx-auto w-full max-w-5xl">
        <nav aria-label="Main navigation" className="mb-6 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3 text-slate-900">
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600 text-white shadow-sm">
              <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
                <rect x="3" y="7" width="18" height="13" rx="2.5" />
                <path d="M8 7V5.5A1.5 1.5 0 0 1 9.5 4h5A1.5 1.5 0 0 1 16 5.5V7M3 12h18m-11 0v2h4v-2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </span>
            <span className="text-base font-bold tracking-tight sm:text-lg">AI Job Matching</span>
          </Link>
          <Link href="/jobs" className="rounded-lg px-3 py-2 text-sm font-semibold text-slate-600 transition hover:bg-white hover:text-indigo-700">
            Browse jobs
          </Link>
        </nav>

        <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl shadow-slate-200/70 lg:grid lg:grid-cols-2">
          <div className="relative overflow-hidden bg-gradient-to-r from-slate-950 via-indigo-950 to-indigo-800 px-6 py-6 text-white lg:hidden sm:px-10">
            <div aria-hidden="true" className="absolute -right-8 -top-16 h-40 w-40 rounded-full border-[20px] border-white/5" />
            <p className="relative text-[10px] font-semibold tracking-[0.18em] text-indigo-200">AI-POWERED CAREER MATCHING</p>
            <h2 className="relative mt-2 max-w-sm text-xl font-semibold tracking-tight sm:text-2xl">Find work that fits who you are.</h2>
          </div>
          <aside className="relative hidden overflow-hidden bg-gradient-to-br from-slate-950 via-indigo-950 to-indigo-800 p-10 text-white lg:flex lg:min-h-[560px] lg:flex-col xl:p-12">
            <div aria-hidden="true" className="absolute -right-24 -top-24 h-72 w-72 rounded-full border-[36px] border-white/5" />
            <div aria-hidden="true" className="absolute -bottom-32 -left-24 h-80 w-80 rounded-full border-[48px] border-white/5" />
            <div className="relative">
              <span className="inline-flex items-center gap-2 rounded-full border border-indigo-300/20 bg-indigo-300/10 px-3 py-1.5 text-xs font-semibold tracking-wide text-indigo-100">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                YOUR NEXT CHAPTER STARTS HERE
              </span>
              <h2 className="mt-7 max-w-sm text-4xl font-semibold leading-tight tracking-tight xl:text-[2.75rem]">
                Find work that fits who you are.
              </h2>
              <p className="mt-4 max-w-sm text-base leading-7 text-indigo-100/75">
                Pick up where you left off and find opportunities that match your strengths.
              </p>
            </div>

            <div className="relative mt-10 rounded-2xl border border-white/15 bg-white/[0.09] p-5 shadow-2xl shadow-slate-950/20 backdrop-blur-sm">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-indigo-100/75">A glimpse of what’s possible</span>
                <span className="rounded-full bg-emerald-300/15 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wider text-emerald-200">Great fit</span>
              </div>
              <div className="mt-5 flex items-start justify-between gap-3">
                <div className="flex items-center gap-3">
                  <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-amber-300 to-orange-400 text-sm font-bold text-slate-950">A</span>
                  <div>
                    <p className="font-semibold text-white">Product Designer</p>
                    <p className="mt-1 text-sm text-indigo-100/65">Acme Studio · Remote</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-semibold tracking-tight text-emerald-300">92%</p>
                  <p className="text-[10px] uppercase tracking-wider text-indigo-100/60">match</p>
                </div>
              </div>
              <div className="mt-5 flex flex-wrap gap-2">
                <span className="rounded-lg border border-white/10 bg-white/[0.07] px-2.5 py-1.5 text-xs text-indigo-50/85">Product design</span>
                <span className="rounded-lg border border-white/10 bg-white/[0.07] px-2.5 py-1.5 text-xs text-indigo-50/85">Figma</span>
                <span className="rounded-lg border border-white/10 bg-white/[0.07] px-2.5 py-1.5 text-xs text-indigo-50/85">User research</span>
              </div>
            </div>

            <p className="relative mt-auto pt-8 text-xs leading-5 text-indigo-100/55">
              Better matches begin with a clearer picture of your skills.
            </p>
          </aside>

          <section className="px-6 py-9 sm:px-10 sm:py-12 lg:px-12 lg:py-14">
            <div className="mx-auto w-full max-w-md">
              <div className="mb-8">
                <p className="text-sm font-semibold text-indigo-600">Welcome back</p>
                <h1 className="mt-2 text-3xl font-semibold tracking-tight text-slate-950">Sign in to your account</h1>
                <p className="mt-2 text-sm leading-6 text-slate-500">Enter your details to access your personalized job matches.</p>
              </div>

              {error && (
                <div role="alert" className="mb-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm leading-6 text-red-700">
                  {error}
                </div>
              )}

              {notice && (
                <div role="status" className="mb-5 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm leading-6 text-emerald-800">
                  {notice}
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-5">
                <div>
                  <label htmlFor="email" className="mb-2 block text-sm font-semibold text-slate-700">Email address</label>
                  <input
                    id="email"
                    type="email"
                    autoComplete="email"
                    required
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-slate-900 outline-none transition placeholder:text-slate-400 hover:border-slate-400 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10"
                    placeholder="you@example.com"
                  />
                </div>

                <div>
                  <div className="mb-2 flex items-center justify-between">
                    <label htmlFor="password" className="block text-sm font-semibold text-slate-700">Password</label>
                    <Link href="/forgot-password" className="text-sm font-semibold text-indigo-600 transition hover:text-indigo-700">
                      Forgot password?
                    </Link>
                  </div>
                  <input
                    id="password"
                    type="password"
                    autoComplete="current-password"
                    required
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-slate-900 outline-none transition placeholder:text-slate-400 hover:border-slate-400 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10"
                    placeholder="Enter your password"
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="flex w-full items-center justify-center rounded-xl bg-indigo-600 px-4 py-3.5 font-semibold text-white shadow-sm shadow-indigo-600/20 transition hover:bg-indigo-700 focus:outline-none focus:ring-4 focus:ring-indigo-500/25 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {loading ? 'Signing in...' : 'Sign in'}
                </button>
              </form>

              <p className="mt-8 text-center text-sm text-slate-600">
                New to AI Job Matching?{' '}
                <Link href="/register" className="font-semibold text-indigo-600 transition hover:text-indigo-700">Create an account</Link>
              </p>
            </div>
          </section>
        </div>

        <p className="mt-6 text-center text-xs text-slate-400">Connecting people with opportunities.</p>
      </div>
    </main>
  );
}
