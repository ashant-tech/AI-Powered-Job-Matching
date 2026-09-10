"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import CVUploader from "@/components/CVUploader";
import SkillBadge from "@/components/SkillBadge";
import { deleteCV, listCVs } from "@/services/cvApi";
import type { CV } from "@/types/CV";

export default function UploadCVPage() {
  const [cvs, setCvs] = useState<CV[]>([]);
  const [latest, setLatest] = useState<CV | null>(null);

  useEffect(() => {
    listCVs().then(setCvs).catch(() => undefined);
  }, []);

  return (
    <AppShell title="Upload CV">
      <div className="grid gap-6 lg:grid-cols-2">
        <CVUploader
          onUploaded={(cv) => {
            setLatest(cv);
            setCvs((prev) => [cv, ...prev]);
          }}
        />
        {latest && (
          <div className="card space-y-3">
            <h2 className="font-semibold">Analysis of {latest.file_name}</h2>
            <p className="text-sm text-slate-700">{latest.summary}</p>
            <div className="flex flex-wrap gap-1.5">
              {latest.skills.map((s) => (
                <SkillBadge key={s.id} name={s.name} />
              ))}
            </div>
            {latest.education.length > 0 && (
              <ul className="list-inside list-disc text-sm text-slate-700">
                {latest.education.map((e) => (
                  <li key={e}>{e}</li>
                ))}
              </ul>
            )}
            <Link href="/recommendations" className="btn-primary">
              Find matching jobs →
            </Link>
          </div>
        )}
      </div>

      {cvs.length > 0 && (
        <section className="card">
          <h2 className="mb-3 font-semibold">Uploaded CVs</h2>
          <ul className="divide-y divide-slate-200">
            {cvs.map((cv) => (
              <li key={cv.id} className="flex items-center justify-between py-2 text-sm">
                <span>
                  {cv.file_name} <span className="text-slate-500">· {cv.skills.length} skills</span>
                </span>
                <button
                  className="text-rose-600 hover:underline"
                  onClick={async () => {
                    await deleteCV(cv.id);
                    setCvs((prev) => prev.filter((c) => c.id !== cv.id));
                  }}
                >
                  Delete
                </button>
              </li>
            ))}
          </ul>
        </section>
      )}
    </AppShell>
  );
}
