export interface Job {
  external_id: string;
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
  apply_url: string;
  deadline?: string;
}

