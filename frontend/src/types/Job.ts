import type { Skill } from "./CV";

export interface Job {
  id: number;
  title: string;
  company: string;
  location: string;
  description: string;
  requirements: string;
  salary_range: string | null;
  job_type: string;
  source: string;
  source_url: string | null;
  min_years_experience: number;
  is_active: boolean;
  posted_at: string;
  skills: Skill[];
}
