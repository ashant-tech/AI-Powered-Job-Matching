export interface CV {
  id: number;
  user_id: number;
  title: string;
  file_path: string;
  file_name: string;
  parsed_text?: string;
  skills?: string;
  experience?: string;
  education?: string;
  created_at: string;
  updated_at?: string;
}

export interface CVCreate {
  title: string;
}

export interface CVAnalysis {
  skills: string[];
  experience: any[];
  education: any[];
  summary: string;
}
