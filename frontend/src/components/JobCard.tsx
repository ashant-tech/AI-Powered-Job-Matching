import type { Job } from "@/types/Job";
import SkillBadge from "./SkillBadge";

export default function JobCard({ job, children }: { job: Job; children?: React.ReactNode }) {
  return (
    <article className="card flex flex-col gap-3">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold text-slate-900">{job.title}</h3>
          <p className="text-sm text-slate-600">
            {job.company}
            {job.location && <span> · {job.location}</span>}
            <span> · {job.job_type}</span>
          </p>
        </div>
        {children}
      </div>
      <p className="line-clamp-3 text-sm text-slate-700">{job.description}</p>
      {job.skills.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {job.skills.slice(0, 8).map((s) => (
            <SkillBadge key={s.id} name={s.name} />
          ))}
        </div>
      )}
      <div className="flex items-center justify-between text-xs text-slate-500">
        <span>{job.salary_range ?? "Salary not specified"}</span>
        {job.source_url ? (
          <a href={job.source_url} target="_blank" rel="noreferrer" className="font-medium text-indigo-600 hover:underline">
            View posting →
          </a>
        ) : (
          <span>Source: {job.source}</span>
        )}
      </div>
    </article>
  );
}
