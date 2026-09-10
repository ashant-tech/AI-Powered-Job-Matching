export interface Skill {
  id: number;
  name: string;
}

export interface CV {
  id: number;
  user_id: number;
  file_name: string;
  summary: string;
  education: string[];
  experience: string[];
  years_of_experience: number;
  skills: Skill[];
  created_at: string;
}
