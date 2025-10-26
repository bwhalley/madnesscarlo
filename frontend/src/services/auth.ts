/**
 * Authentication Service
 * Handles user registration, login, and token management
 */

import api from './api';

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  full_name: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    username: string;
    full_name: string;
    is_active: boolean;
    is_verified: boolean;
    created_at: string;
  };
}

class AuthService {
  private accessToken: string | null = null;
  private refreshToken: string | null = null;
  private user: any = null;

  constructor() {
    // Load tokens from localStorage on initialization
    this.accessToken = localStorage.getItem('access_token');
    this.refreshToken = localStorage.getItem('refresh_token');
    const userStr = localStorage.getItem('user');
    if (userStr) {
      this.user = JSON.parse(userStr);
    }

    // Set up axios interceptor to add token to requests
    api.interceptors.request.use((config) => {
      if (this.accessToken) {
        config.headers.Authorization = `Bearer ${this.accessToken}`;
      }
      return config;
    });
  }

  async register(data: RegisterData): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/api/auth/register', data);
    this.setAuth(response.data);
    return response.data;
  }

  async login(data: LoginData): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/api/auth/login', {
      email: data.email,
      password: data.password,
    });
    this.setAuth(response.data);
    return response.data;
  }

  async getCurrentUser() {
    if (!this.accessToken) {
      throw new Error('Not authenticated');
    }
    const response = await api.get('/api/auth/me');
    this.user = response.data;
    localStorage.setItem('user', JSON.stringify(this.user));
    return response.data;
  }

  logout() {
    this.accessToken = null;
    this.refreshToken = null;
    this.user = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  }

  isAuthenticated(): boolean {
    return !!this.accessToken;
  }

  getUser() {
    return this.user;
  }

  getAccessToken(): string | null {
    return this.accessToken;
  }

  private setAuth(data: AuthResponse) {
    this.accessToken = data.access_token;
    this.refreshToken = data.refresh_token;
    this.user = data.user;

    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    localStorage.setItem('user', JSON.stringify(data.user));
  }
}

export const authService = new AuthService();

