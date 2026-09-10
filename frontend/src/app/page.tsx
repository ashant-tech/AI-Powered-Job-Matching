import Link from "next/link";

const steps = [
  { title: "Upload your CV", body: "PDF or Word. Our AI reads your skills, education and experience in seconds." },
  { title: "Get matched", body: "Every job is scored against your profile with a transparent skill and experience breakdown." },
  { title: "Stay notified", body: "We keep collecting jobs and alert you the moment a strong match appears." },
];

export default function LandingPage() {
  return (
    <main>
      <section className="mx-auto max-w-6xl px-4 py-24 text-center">
        <p className="mb-4 text-sm font-semibold uppercase tracking-wide text-indigo-600">AI Job Matching</p>
        <h1 className="mx-auto max-w-3xl text-4xl font-extrabold tracking-tight text-slate-900 sm:text-6xl">
          Stop searching. Let the right jobs find you.
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-600">
          Upload your CV once. We analyze your qualifications, search job opportunities for you and notify you when
          something fits.
        </p>
        <div className="mt-10 flex justify-center gap-3">
          <Link href="/register" className="btn-primary px-6 py-3 text-base">
            Upload your CV
          </Link>
          <Link href="/jobs" className="btn-secondary px-6 py-3 text-base">
            Browse jobs
          </Link>
        </div>
      </section>
      <section className="border-t border-slate-200 bg-white">
        <div className="mx-auto grid max-w-6xl gap-8 px-4 py-16 md:grid-cols-3">
          {steps.map((s, i) => (
            <div key={s.title} className="space-y-2">
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-indigo-600 font-bold text-white">
                {i + 1}
              </div>
              <h3 className="text-lg font-semibold">{s.title}</h3>
              <p className="text-slate-600">{s.body}</p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
