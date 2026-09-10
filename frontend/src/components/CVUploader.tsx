"use client";

import { useRef, useState } from "react";
import type { CV } from "@/types/CV";
import { uploadCV } from "@/services/cvApi";
import { ApiError } from "@/services/apiClient";

export default function CVUploader({ onUploaded }: { onUploaded: (cv: CV) => void }) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);

  async function submit() {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      onUploaded(await uploadCV(file));
      setFile(null);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Upload failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card space-y-4">
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          const dropped = e.dataTransfer.files[0];
          if (dropped) setFile(dropped);
        }}
        onClick={() => inputRef.current?.click()}
        className={`flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed p-10 text-center transition ${
          dragging ? "border-indigo-500 bg-indigo-50" : "border-slate-300 hover:border-indigo-400"
        }`}
      >
        <p className="font-medium text-slate-800">{file ? file.name : "Drop your CV here or click to browse"}</p>
        <p className="mt-1 text-xs text-slate-500">PDF, DOCX or TXT · max 10MB</p>
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx,.txt"
          className="hidden"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        />
      </div>
      {error && <p className="text-sm text-rose-600">{error}</p>}
      <button className="btn-primary w-full" disabled={!file || loading} onClick={submit}>
        {loading ? "Analyzing CV…" : "Upload & analyze"}
      </button>
    </div>
  );
}
