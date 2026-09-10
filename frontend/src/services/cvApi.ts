import type { CV } from "@/types/CV";
import { request } from "./apiClient";

export function uploadCV(file: File) {
  const body = new FormData();
  body.append("file", file);
  return request<CV>("/api/cv/upload", { method: "POST", body });
}

export function listCVs() {
  return request<CV[]>("/api/cv");
}

export function getLatestCV() {
  return request<CV | null>("/api/cv/latest");
}

export function deleteCV(id: number) {
  return request<void>(`/api/cv/${id}`, { method: "DELETE" });
}
