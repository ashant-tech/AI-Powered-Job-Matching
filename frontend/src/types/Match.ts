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
  detailed_reasons?: string[];
  fit_level?: 'Strong' | 'Good' | 'Possible';
  score_confidence?: number;
  match_caveats?: string[];
  component_scores?: Record<string, number | null>;
  cv_match_score?: number;
  feedback_adjustment?: number;
  skill_gaps?: {
    missing_skills: string[];
    matched_skills?: string[];
    recommended_skills: string[];
    gap_percentage: number;
  };
}

export type MatchStatus = 'pending' | 'viewed' | 'applied' | 'rejected' | 'relevant' | 'not_relevant';

export interface MatchUpdate {
  status: MatchStatus;
}
