import Link from 'next/link';

function BriefcaseIcon({ className = 'h-5 w-5' }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
      <rect x="3" y="7" width="18" height="13" rx="2.5" />
      <path d="M8 7V5.5A1.5 1.5 0 0 1 9.5 4h5A1.5 1.5 0 0 1 16 5.5V7M3 12h18m-11 0v2h4v-2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export default function Home() {
  return (
    <main className="min-h-screen bg-white text-slate-900">
      <section className="relative overflow-hidden bg-slate-950 text-white">
        <div aria-hidden="true" className="absolute -right-40 -top-64 h-[42rem] w-[42rem] rounded-full border border-indigo-300/10" />
        <div aria-hidden="true" className="absolute -right-20 -top-44 h-[34rem] w-[34rem] rounded-full border border-indigo-300/[0.08]" />
        <div aria-hidden="true" className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(79,70,229,0.28),transparent_52%)]" />

        <div className="relative mx-auto max-w-7xl px-5 pb-20 pt-5 sm:px-8 sm:pb-24 lg:px-10">
          <header className="flex items-center justify-between">
            <Link href="/" className="flex items-center gap-3 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-indigo-300">
              <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500 shadow-lg shadow-indigo-950/40">
                <BriefcaseIcon />
              </span>
              <span className="text-base font-bold tracking-tight sm:text-lg">AI Job Matching</span>
            </Link>

            <nav aria-label="Main navigation" className="flex items-center gap-2 sm:gap-5">
              <Link href="/jobs" className="hidden rounded-lg px-3 py-2 text-sm font-medium text-slate-300 transition hover:bg-white/5 hover:text-white sm:inline-flex">
                Browse jobs
              </Link>
              <Link href="/login" className="rounded-lg px-3 py-2 text-sm font-semibold text-slate-200 transition hover:text-white">
                Sign in
              </Link>
              <Link href="/register" className="rounded-lg bg-white px-4 py-2.5 text-sm font-semibold text-slate-900 shadow-sm transition hover:bg-indigo-50 focus:outline-none focus:ring-4 focus:ring-white/20">
                Get started
              </Link>
            </nav>
          </header>

          <div className="grid items-center gap-14 pt-16 sm:pt-20 lg:grid-cols-[1.05fr_0.95fr] lg:gap-10 lg:pt-24">
            <div className="max-w-2xl">
              <div className="inline-flex items-center gap-2 rounded-full border border-indigo-300/20 bg-indigo-300/[0.08] px-3.5 py-2 text-xs font-semibold tracking-wide text-indigo-100 sm:text-sm">
                <span className="h-2 w-2 rounded-full bg-emerald-400" />
                A clearer path to your next opportunity
              </div>
              <h1 className="mt-7 text-4xl font-semibold leading-[1.12] tracking-tight text-white sm:text-5xl lg:text-6xl">
                Find the work that fits <span className="text-indigo-300">you.</span>
              </h1>
              <p className="mt-6 max-w-xl text-base leading-7 text-slate-300 sm:text-lg sm:leading-8">
                Explore opportunities across Ethiopia, or create a profile to discover roles based on your experience and skills.
              </p>

              <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                <Link href="/register" className="inline-flex items-center justify-center gap-2 rounded-xl bg-indigo-500 px-6 py-3.5 text-sm font-semibold text-white shadow-lg shadow-indigo-950/40 transition hover:bg-indigo-400 focus:outline-none focus:ring-4 focus:ring-indigo-300/30">
                  Create your free account
                  <svg viewBox="0 0 20 20" fill="none" className="h-4 w-4" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
                    <path d="M4 10h12m-5-5 5 5-5 5" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </Link>
                <Link href="/jobs" className="inline-flex items-center justify-center rounded-xl border border-white/15 bg-white/[0.04] px-6 py-3.5 text-sm font-semibold text-white transition hover:border-white/25 hover:bg-white/[0.08] focus:outline-none focus:ring-4 focus:ring-white/10">
                  Browse open jobs
                </Link>
              </div>

              <div className="mt-8 flex flex-wrap gap-x-6 gap-y-3 text-sm text-slate-300">
                <span className="inline-flex items-center gap-2">
                  <svg viewBox="0 0 20 20" fill="none" className="h-4 w-4 text-emerald-300" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                    <path d="m4 10 4 4 8-8" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                  Browse without an account
                </span>
                <span className="inline-flex items-center gap-2">
                  <svg viewBox="0 0 20 20" fill="none" className="h-4 w-4 text-emerald-300" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                    <path d="m4 10 4 4 8-8" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                  Personalized job discovery
                </span>
              </div>
            </div>

            <div className="relative mx-auto w-full max-w-lg lg:ml-auto">
              <div aria-hidden="true" className="absolute -inset-5 rounded-[2rem] bg-indigo-500/10 blur-2xl" />
              <div className="relative rounded-2xl border border-white/10 bg-white/[0.07] p-4 shadow-2xl shadow-black/30 backdrop-blur sm:p-6">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="text-sm font-medium text-indigo-200">Your job search</p>
                    <h2 className="mt-1 text-xl font-semibold tracking-tight text-white">A better place to begin</h2>
                  </div>
                  <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-400/15 text-indigo-200">
                    <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
                      <circle cx="10.8" cy="10.8" r="6.8" />
                      <path d="m16 16 4 4" strokeLinecap="round" />
                    </svg>
                  </span>
                </div>

                <div className="mt-6 flex items-center gap-3 rounded-xl border border-white/10 bg-slate-950/40 px-4 py-3.5">
                  <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5 shrink-0 text-slate-400" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
                    <circle cx="10.8" cy="10.8" r="6.8" />
                    <path d="m16 16 4 4" strokeLinecap="round" />
                  </svg>
                  <span className="text-sm text-slate-400">Role, skill, or company</span>
                  <span className="ml-auto rounded-lg bg-indigo-500 px-3 py-2 text-xs font-semibold text-white">Search</span>
                </div>

                <div className="mt-5 flex items-center justify-between">
                  <p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-400">A few fields to explore</p>
                  <Link href="/jobs" className="text-xs font-semibold text-indigo-200 transition hover:text-white">View jobs</Link>
                </div>

                <div className="mt-3 space-y-3">
                  <div className="flex items-center gap-3 rounded-xl border border-white/10 bg-white/[0.04] p-3.5">
                    <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-sky-300/10 text-sky-200">
                      <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" stroke="currentColor" strokeWidth="1.7" aria-hidden="true">
                        <rect x="4" y="4" width="16" height="16" rx="3" />
                        <path d="M8 9h8M8 12h8M8 15h5" strokeLinecap="round" />
                      </svg>
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-semibold text-white">Technology &amp; IT</p>
                      <p className="mt-0.5 text-xs text-slate-400">Software, data, support, and more</p>
                    </div>
                    <svg viewBox="0 0 20 20" fill="none" className="h-4 w-4 text-slate-500" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
                      <path d="m7 4 6 6-6 6" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </div>

                  <div className="flex items-center gap-3 rounded-xl border border-white/10 bg-white/[0.04] p-3.5">
                    <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-amber-300/10 text-amber-200">
                      <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" stroke="currentColor" strokeWidth="1.7" aria-hidden="true">
                        <path d="M3.5 20h17M5 20V9l7-5 7 5v11M9 12h.01M15 12h.01M9 16h.01M15 16h.01M11 20v-3h2v3" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-semibold text-white">Business &amp; Finance</p>
                      <p className="mt-0.5 text-xs text-slate-400">Operations, accounting, and more</p>
                    </div>
                    <svg viewBox="0 0 20 20" fill="none" className="h-4 w-4 text-slate-500" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
                      <path d="m7 4 6 6-6 6" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </div>

                  <div className="flex items-center gap-3 rounded-xl border border-white/10 bg-white/[0.04] p-3.5">
                    <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-rose-300/10 text-rose-200">
                      <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" stroke="currentColor" strokeWidth="1.7" aria-hidden="true">
                        <path d="M4 20h16M6 20V8l6-4 6 4v12M9 11h.01M15 11h.01M9 15h.01M15 15h.01M11 20v-2h2v2" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-semibold text-white">Education &amp; Training</p>
                      <p className="mt-0.5 text-xs text-slate-400">Teaching, research, and more</p>
                    </div>
                    <svg viewBox="0 0 20 20" fill="none" className="h-4 w-4 text-slate-500" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
                      <path d="m7 4 6 6-6 6" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </div>
                </div>

                <p className="mt-4 text-center text-xs text-slate-400">Illustrative preview · Explore current listings</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-5 py-16 sm:px-8 sm:py-20 lg:px-10">
        <div className="max-w-2xl">
          <p className="text-sm font-semibold text-indigo-600">Designed around your search</p>
          <h2 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950 sm:text-4xl">From browsing to a better fit.</h2>
          <p className="mt-4 text-base leading-7 text-slate-600">
            Find opportunities, organize your search, and use your profile to get recommendations that are more relevant to your experience.
          </p>
        </div>

        <div className="mt-10 grid gap-5 md:grid-cols-3">
          <article className="group rounded-2xl border border-slate-200 bg-white p-6 transition hover:-translate-y-1 hover:border-indigo-200 hover:shadow-xl hover:shadow-slate-200/60">
            <span className="flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600">
              <svg viewBox="0 0 24 24" fill="none" className="h-6 w-6" stroke="currentColor" strokeWidth="1.7" aria-hidden="true">
                <circle cx="10.8" cy="10.8" r="6.8" />
                <path d="m16 16 4 4" strokeLinecap="round" />
              </svg>
            </span>
            <h3 className="mt-5 text-lg font-semibold text-slate-900">Search with purpose</h3>
            <p className="mt-2 text-sm leading-6 text-slate-600">Filter job listings by field, location, role type, and other details that matter to you.</p>
          </article>

          <article className="group rounded-2xl border border-slate-200 bg-white p-6 transition hover:-translate-y-1 hover:border-indigo-200 hover:shadow-xl hover:shadow-slate-200/60">
            <span className="flex h-12 w-12 items-center justify-center rounded-xl bg-sky-50 text-sky-600">
              <svg viewBox="0 0 24 24" fill="none" className="h-6 w-6" stroke="currentColor" strokeWidth="1.7" aria-hidden="true">
                <path d="M12 3.5 14.6 9l5.9.8-4.3 4.1 1 5.8-5.2-2.8-5.2 2.8 1-5.8-4.3-4.1 5.9-.8L12 3.5Z" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </span>
            <h3 className="mt-5 text-lg font-semibold text-slate-900">Discover relevant roles</h3>
            <p className="mt-2 text-sm leading-6 text-slate-600">Add your experience and skills to your profile to help surface opportunities that fit.</p>
          </article>

          <article className="group rounded-2xl border border-slate-200 bg-white p-6 transition hover:-translate-y-1 hover:border-indigo-200 hover:shadow-xl hover:shadow-slate-200/60">
            <span className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600">
              <svg viewBox="0 0 24 24" fill="none" className="h-6 w-6" stroke="currentColor" strokeWidth="1.7" aria-hidden="true">
                <path d="M7 3.5h7l4 4V20a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4.5a1 1 0 0 1 1-1Z" strokeLinejoin="round" />
                <path d="M14 4v4h4M9 13h6M9 16h6" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </span>
            <h3 className="mt-5 text-lg font-semibold text-slate-900">Keep your search organized</h3>
            <p className="mt-2 text-sm leading-6 text-slate-600">Save your profile, review matches, and return to your job search when you’re ready.</p>
          </article>
        </div>
      </section>

      <section className="border-y border-slate-200 bg-slate-50">
        <div className="mx-auto max-w-7xl px-5 py-16 sm:px-8 sm:py-20 lg:px-10">
          <div className="grid gap-10 lg:grid-cols-[0.8fr_1.2fr] lg:items-center">
            <div>
              <p className="text-sm font-semibold text-indigo-600">A simple place to start</p>
              <h2 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950 sm:text-4xl">Your next step, made clearer.</h2>
              <p className="mt-4 text-base leading-7 text-slate-600">Start with a search today. Create an account whenever you’re ready for a more personalized experience.</p>
              <Link href="/jobs" className="mt-6 inline-flex items-center gap-2 font-semibold text-indigo-700 transition hover:text-indigo-900">
                Explore available jobs
                <svg viewBox="0 0 20 20" fill="none" className="h-4 w-4" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
                  <path d="M4 10h12m-5-5 5 5-5 5" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </Link>
            </div>

            <div className="grid gap-4 sm:grid-cols-3">
              <div className="rounded-2xl border border-slate-200 bg-white p-5">
                <span className="flex h-9 w-9 items-center justify-center rounded-full bg-indigo-50 text-sm font-semibold text-indigo-700">01</span>
                <h3 className="mt-4 font-semibold text-slate-900">Explore</h3>
                <p className="mt-2 text-sm leading-6 text-slate-600">Browse roles by field and location.</p>
              </div>
              <div className="rounded-2xl border border-slate-200 bg-white p-5">
                <span className="flex h-9 w-9 items-center justify-center rounded-full bg-indigo-50 text-sm font-semibold text-indigo-700">02</span>
                <h3 className="mt-4 font-semibold text-slate-900">Create a profile</h3>
                <p className="mt-2 text-sm leading-6 text-slate-600">Share the experience and skills you bring.</p>
              </div>
              <div className="rounded-2xl border border-slate-200 bg-white p-5">
                <span className="flex h-9 w-9 items-center justify-center rounded-full bg-indigo-50 text-sm font-semibold text-indigo-700">03</span>
                <h3 className="mt-4 font-semibold text-slate-900">Find your fit</h3>
                <p className="mt-2 text-sm leading-6 text-slate-600">Review personalized job recommendations.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-5 py-16 sm:px-8 sm:py-20 lg:px-10">
        <div className="overflow-hidden rounded-3xl bg-gradient-to-br from-indigo-700 via-indigo-700 to-slate-900 px-6 py-10 text-center shadow-xl shadow-indigo-950/10 sm:px-12 sm:py-14">
          <p className="text-sm font-semibold text-indigo-200">A good opportunity can start with one search</p>
          <h2 className="mx-auto mt-3 max-w-2xl text-3xl font-semibold tracking-tight text-white sm:text-4xl">Ready to explore what’s next?</h2>
          <p className="mx-auto mt-4 max-w-xl text-base leading-7 text-indigo-100">Browse current opportunities or create an account to start building your personalized job search.</p>
          <div className="mt-7 flex flex-col justify-center gap-3 sm:flex-row">
            <Link href="/jobs" className="inline-flex items-center justify-center rounded-xl bg-white px-6 py-3.5 text-sm font-semibold text-indigo-800 transition hover:bg-indigo-50 focus:outline-none focus:ring-4 focus:ring-white/25">
              Browse jobs
            </Link>
            <Link href="/register" className="inline-flex items-center justify-center rounded-xl border border-white/25 bg-white/10 px-6 py-3.5 text-sm font-semibold text-white transition hover:bg-white/15 focus:outline-none focus:ring-4 focus:ring-white/20">
              Create an account
            </Link>
          </div>
        </div>
      </section>

      <footer className="border-t border-slate-200">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-5 py-7 text-sm text-slate-500 sm:flex-row sm:items-center sm:justify-between sm:px-8 lg:px-10">
          <Link href="/" className="flex items-center gap-2 font-semibold text-slate-800">
            <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-600 text-white"><BriefcaseIcon className="h-4 w-4" /></span>
            AI Job Matching
          </Link>
          <p>Explore opportunities and take your next career step.</p>
          <nav aria-label="Footer navigation" className="flex gap-5">
            <Link href="/jobs" className="transition hover:text-indigo-700">Browse jobs</Link>
            <Link href="/login" className="transition hover:text-indigo-700">Sign in</Link>
          </nav>
        </div>
      </footer>
    </main>
  );
}
