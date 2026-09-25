import { Job } from './Job';

export interface Match {
  id: number;
  user_id: number;
  cv_id: number;
  external_job_id: string;
  match_score: number;
  match_reasons?: string;
  status: string;
  created_at: string;
  updated_at?: string;
  job?: Job;
}

export interface MatchUpdate {
  status: string;
}
