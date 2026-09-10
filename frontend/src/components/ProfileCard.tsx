import type { User } from "@/types/User";
import type { CV } from "@/types/CV";
import SkillBadge from "./SkillBadge";

export default function ProfileCard({ user, cv }: { user: User; cv: CV | null }) {
  return (
    <section className="card space-y-4">
      <div className="flex items-center gap-4">
        <div className="flex h-14 w-14 items-center justify-center rounded-full bg-indigo-100 text-xl font-bold text-indigo-700">
          {user.full_name.charAt(0).toUpperCase()}
        </div>
        <div>
          <h2 className="text-lg font-semibold">{user.full_name}</h2>
          <p className="text-sm text-slate-600">{user.email}</p>
          {user.phone && <p className="text-sm text-slate-600">{user.phone}</p>}
        </div>
      </div>
      {cv ? (
        <div className="space-y-3 text-sm">
          <p className="text-slate-700">{cv.summary}</p>
          <p>
            <span className="font-medium">Experience:</span> ~{cv.years_of_experience} years
          </p>
          {cv.education.length > 0 && (
            <div>
              <p className="font-medium">Education</p>
              <ul className="list-inside list-disc text-slate-700">
                {cv.education.map((e) => (
                  <li key={e}>{e}</li>
                ))}
              </ul>
            </div>
          )}
          <div>
            <p className="mb-1 font-medium">Skills ({cv.skills.length})</p>
            <div className="flex flex-wrap gap-1.5">
              {cv.skills.map((s) => (
                <SkillBadge key={s.id} name={s.name} />
              ))}
            </div>
          </div>
          <p className="text-xs text-slate-500">
            From {cv.file_name} · uploaded {new Date(cv.created_at).toLocaleDateString()}
          </p>
        </div>
      ) : (
        <p className="text-sm text-slate-600">No CV uploaded yet.</p>
      )}
    </section>
  );
}
