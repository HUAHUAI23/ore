export interface User {
  id: number;
  name: string;
  nickname: string;
  email: string | null;
  phone: string | null;
  is_active: boolean;
  created_at: string;
  last_login: string | null;
}

export interface LoginRequest {
  name: string;
  password: string;
}

export interface RegisterRequest {
  name: string;
  password: string;
  nickname?: string;
  email?: string;
  phone?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}
