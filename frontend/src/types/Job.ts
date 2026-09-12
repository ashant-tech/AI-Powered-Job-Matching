export interface Job {
  id: number;
  title: string;
  company: string;
  description: string;
  requirements?: string;
  skills?: string;
  location?: string;
  salary_min?: number;
  salary_max?: number;
  job_type?: string;
  source?: string;
  source_url?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface JobCreate {
  title: string;
  company: string;
  description: string;
  location?: string;
  salary_min?: number;
  salary_max?: number;
  job_type?: string;
  requirements?: string;
  skills?: string;
  source?: string;
  source_url?: string;
}
