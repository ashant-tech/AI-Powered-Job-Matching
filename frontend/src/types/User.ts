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
  telegram_chat_id?: string;
  telegram_notifications_enabled?: boolean;
  telegram_username?: string;
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
  telegram_chat_id?: string;
  telegram_username?: string;
  telegram_notifications_enabled?: boolean;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface TelegramNotificationRequest {
  chat_id: string;
  telegram_username?: string;
}

export interface TelegramNotificationStatus {
  enabled: boolean;
  chat_id?: string;
  telegram_username?: string;
}
