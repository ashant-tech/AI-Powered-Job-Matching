export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  phone?: string;
  is_active: boolean;
  is_seeker: boolean;
  created_at: string;
  updated_at?: string;
  profile?: string;
}

export interface UserCreate {
  email: string;
  username: string;
  password: string;
  full_name?: string;
  phone?: string;
  is_seeker?: boolean;
}

export interface UserUpdate {
  full_name?: string;
  phone?: string;
  profile?: string;
}

export interface UserLogin {
  email: string;
  password: string;
}
