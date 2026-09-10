export interface User {
  id: number;
  email: string;
  full_name: string;
  phone: string | null;
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}
