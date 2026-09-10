import type { Job } from "@/types/Job";
import { request } from "./apiClient";

export function listJobs(params: { q?: string; location?: string; limit?: number; offset?: number } = {}) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== "") search.set(k, String(v));
  });
  const qs = search.toString();
  return request<Job[]>(`/api/jobs${qs ? `?${qs}` : ""}`);
}

export function getJob(id: number) {
  return request<Job>(`/api/jobs/${id}`);
}
