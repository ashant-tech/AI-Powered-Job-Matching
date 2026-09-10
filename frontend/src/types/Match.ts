import type { Job } from "./Job";

export interface Match {
  id: number;
  cv_id: number;
  job_id: number;
  score: number;
  skill_score: number;
  semantic_score: number;
  experience_score: number;
  matched_skills: string[];
  missing_skills: string[];
  created_at: string;
  job: Job;
}

export interface Notification {
  id: number;
  job_id: number | null;
  title: string;
  message: string;
  channel: string;
  is_read: boolean;
  created_at: string;
}
