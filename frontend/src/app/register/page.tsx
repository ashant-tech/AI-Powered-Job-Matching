'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function RegisterPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
    full_name: '',
    phone: '',
    telegram_username: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email,
          username: formData.username,
          password: formData.password,
          full_name: formData.full_name,
          phone: formData.phone,
          telegram_username: formData.telegram_username,
        }),
      });

      if (!response.ok) {
        const responseBody = await response.text();
        let message = 'Registration failed';

        try {
          const errorData = JSON.parse(responseBody);
          message = errorData.detail || message;
        } catch {}

        throw new Error(message);
      }

      router.push('/login');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-6 sm:px-6 lg:flex lg:items-center lg:justify-center lg:py-10">
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

        <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl shadow-slate-200/70 lg:grid lg:grid-cols-[0.85fr_1.15fr]">
          <div className="relative overflow-hidden bg-gradient-to-r from-slate-950 via-indigo-950 to-indigo-800 px-6 py-6 text-white lg:hidden sm:px-10">
            <div aria-hidden="true" className="absolute -right-8 -top-16 h-40 w-40 rounded-full border-[20px] border-white/5" />
            <p className="relative text-[10px] font-semibold tracking-[0.18em] text-indigo-200">A BETTER WAY TO FIND WORK</p>
            <h2 className="relative mt-2 max-w-sm text-xl font-semibold tracking-tight sm:text-2xl">Make your next move a great one.</h2>
          </div>
          <aside className="relative hidden overflow-hidden bg-gradient-to-br from-slate-950 via-indigo-950 to-indigo-800 p-10 text-white lg:flex lg:flex-col xl:p-12">
            <div aria-hidden="true" className="absolute -right-24 -top-24 h-72 w-72 rounded-full border-[36px] border-white/5" />
            <div aria-hidden="true" className="absolute -bottom-32 -left-24 h-80 w-80 rounded-full border-[48px] border-white/5" />
            <div className="relative">
              <span className="inline-flex items-center gap-2 rounded-full border border-indigo-300/20 bg-indigo-300/10 px-3 py-1.5 text-xs font-semibold tracking-wide text-indigo-100">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                A BETTER WAY TO FIND WORK
              </span>
              <h2 className="mt-7 max-w-sm text-4xl font-semibold leading-tight tracking-tight xl:text-[2.75rem]">
                Make your next move a great one.
              </h2>
              <p className="mt-4 max-w-sm text-base leading-7 text-indigo-100/75">
                Create your profile and get connected with opportunities that fit your skills and ambitions.
              </p>
            </div>

            <div className="relative mt-9 rounded-2xl border border-white/15 bg-white/[0.09] p-5 shadow-2xl shadow-slate-950/20 backdrop-blur-sm">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-xs font-medium text-indigo-100/70">Your professional profile</p>
                  <p className="mt-1 text-lg font-semibold text-white">A stronger start</p>
                </div>
                <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-300 to-sky-300 text-indigo-950">
                  <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
                    <path d="M12 3.5 14.6 9l5.9.8-4.3 4.1 1 5.8-5.2-2.8-5.2 2.8 1-5.8-4.3-4.1 5.9-.8L12 3.5Z" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </span>
              </div>
              <div className="mt-5 flex items-center gap-3">
                <div className="h-2 flex-1 overflow-hidden rounded-full bg-white/10">
                  <div className="h-full w-3/4 rounded-full bg-gradient-to-r from-indigo-300 to-emerald-300" />
                </div>
                <span className="text-xs font-semibold text-indigo-100">Almost there</span>
              </div>
              <div className="mt-5 flex flex-wrap gap-2">
                <span className="rounded-lg border border-white/10 bg-white/[0.07] px-2.5 py-1.5 text-xs text-indigo-50/85">Your skills</span>
                <span className="rounded-lg border border-white/10 bg-white/[0.07] px-2.5 py-1.5 text-xs text-indigo-50/85">Your experience</span>
                <span className="rounded-lg border border-white/10 bg-white/[0.07] px-2.5 py-1.5 text-xs text-indigo-50/85">Your goals</span>
              </div>
            </div>

            <div className="relative mt-4 flex items-center gap-3 rounded-xl border border-emerald-300/15 bg-emerald-300/[0.08] px-4 py-3">
              <span className="flex h-9 w-9 items-center justify-center rounded-full bg-emerald-300/15 text-emerald-200">
                <svg viewBox="0 0 24 24" fill="none" className="h-4 w-4" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                  <path d="m5 12 4 4L19 6" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </span>
              <div>
                <p className="text-sm font-semibold text-white">Opportunities with purpose</p>
                <p className="mt-0.5 text-xs text-indigo-100/65">Matched to what makes you unique.</p>
              </div>
            </div>
          </aside>

          <section className="px-6 py-8 sm:px-10 sm:py-10 lg:px-12 lg:py-12">
            <div className="mx-auto w-full max-w-xl">
              <div className="mb-7">
                <p className="text-sm font-semibold text-indigo-600">Get started for free</p>
                <h1 className="mt-2 text-3xl font-semibold tracking-tight text-slate-950">Create your account</h1>
                <p className="mt-2 text-sm leading-6 text-slate-500">A few details are all you need to get started.</p>
              </div>

              {error && (
                <div role="alert" className="mb-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm leading-6 text-red-700">
                  {error}
                </div>
              )}

              <form onSubmit={handleSubmit} className="grid grid-cols-1 gap-x-5 gap-y-4 sm:grid-cols-2">
                <div>
                  <label htmlFor="full_name" className="mb-2 block text-sm font-semibold text-slate-700">Full name <span className="font-normal text-slate-400">(optional)</span></label>
                  <input
                    id="full_name"
                    type="text"
                    autoComplete="name"
                    value={formData.full_name}
                    onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                    className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-slate-900 outline-none transition placeholder:text-slate-400 hover:border-slate-400 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10"
                    placeholder="Your name"
                  />
                </div>

                <div>
                  <label htmlFor="username" className="mb-2 block text-sm font-semibold text-slate-700">Username</label>
                  <input
                    id="username"
                    type="text"
                    autoComplete="username"
                    required
                    value={formData.username}
                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                    className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-slate-900 outline-none transition placeholder:text-slate-400 hover:border-slate-400 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10"
                    placeholder="Choose a username"
                  />
                </div>

                <div className="sm:col-span-2">
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
                  <label htmlFor="phone" className="mb-2 block text-sm font-semibold text-slate-700">Phone <span className="font-normal text-slate-400">(optional)</span></label>
                  <input
                    id="phone"
                    type="tel"
                    autoComplete="tel"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-slate-900 outline-none transition placeholder:text-slate-400 hover:border-slate-400 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10"
                    placeholder="+1 234 567 8900"
                  />
                </div>

                <div>
                  <label htmlFor="telegram_username" className="mb-2 block text-sm font-semibold text-slate-700">Telegram <span className="font-normal text-slate-400">(optional)</span></label>
                  <input
                    id="telegram_username"
                    type="text"
                    autoComplete="off"
                    aria-describedby="telegram-help"
                    value={formData.telegram_username}
                    onChange={(e) => setFormData({ ...formData, telegram_username: e.target.value })}
                    className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-slate-900 outline-none transition placeholder:text-slate-400 hover:border-slate-400 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10"
                    placeholder="@username"
                  />
                  <p id="telegram-help" className="mt-1.5 text-xs leading-5 text-slate-500">For job match notifications</p>
                </div>

                <div>
                  <label htmlFor="password" className="mb-2 block text-sm font-semibold text-slate-700">Password</label>
                  <input
                    id="password"
                    type="password"
                    autoComplete="new-password"
                    minLength={8}
                    required
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-slate-900 outline-none transition placeholder:text-slate-400 hover:border-slate-400 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10"
                    placeholder="At least 8 characters"
                  />
                </div>

                <div>
                  <label htmlFor="confirmPassword" className="mb-2 block text-sm font-semibold text-slate-700">Confirm password</label>
                  <input
                    id="confirmPassword"
                    type="password"
                    autoComplete="new-password"
                    minLength={8}
                    required
                    value={formData.confirmPassword}
                    onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                    className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-slate-900 outline-none transition placeholder:text-slate-400 hover:border-slate-400 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10"
                    placeholder="Re-enter your password"
                  />
                </div>

                <div className="pt-2 sm:col-span-2">
                  <button
                    type="submit"
                    disabled={loading}
                    className="flex w-full items-center justify-center rounded-xl bg-indigo-600 px-4 py-3.5 font-semibold text-white shadow-sm shadow-indigo-600/20 transition hover:bg-indigo-700 focus:outline-none focus:ring-4 focus:ring-indigo-500/25 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {loading ? 'Creating account...' : 'Create account'}
                  </button>
                </div>
              </form>

              <p className="mt-7 text-center text-sm text-slate-600">
                Already have an account?{' '}
                <Link href="/login" className="font-semibold text-indigo-600 transition hover:text-indigo-700">Sign in</Link>
              </p>
            </div>
          </section>
        </div>

        <p className="mt-6 text-center text-xs text-slate-400">Connecting people with opportunities.</p>
      </div>
    </main>
  );
}
