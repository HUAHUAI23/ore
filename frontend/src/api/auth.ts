import type { 
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  User
} from '@/types/auth';

import { get, post } from './index';

// Auth API endpoints
export const authApi = {
  // Login user
  login: (data: LoginRequest): Promise<TokenResponse> => {
    return post<TokenResponse>('/login', data);
  },
  
  // Get current user info
  getCurrentUser: (): Promise<User> => {
    return get<User>('/me');
  },
  
  // Register user
  register: (data: RegisterRequest): Promise<TokenResponse> => {
    return post<TokenResponse>('/register', data);
  }
}; 