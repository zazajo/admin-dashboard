import apiClient from '@/lib/api';
import {
  LoginCredentials,
  LoginResponse,
  RegisterData,
  UserProfile,
  UpdateProfileData,
  ChangePasswordData,
} from '@/types';
import Cookies from 'js-cookie';
import { User } from '@/types';

export const authService = {
  // Login
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/api/auth/login/', credentials);
    
    // Save tokens and user to cookies
    Cookies.set('access_token', response.data.access, { expires: 1 }); // 1 day
    Cookies.set('refresh_token', response.data.refresh, { expires: 7 }); // 7 days
    Cookies.set('user', JSON.stringify(response.data.user), { expires: 7 });
    
    return response.data;
  },

  // Logout
  async logout(): Promise<void> {
    const refreshToken = Cookies.get('refresh_token');
    
    try {
      if (refreshToken) {
        await apiClient.post('/api/auth/logout/', {
          refresh_token: refreshToken,
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear cookies regardless of API response
      Cookies.remove('access_token');
      Cookies.remove('refresh_token');
      Cookies.remove('user');
    }
  },

  // Register (if public registration is enabled)
  async register(data: RegisterData): Promise<User> {
    const response = await apiClient.post<User>('/api/auth/register/', data);
    return response.data;
  },

  // Check authentication
  async checkAuth(): Promise<UserProfile> {
    const response = await apiClient.get<{ authenticated: boolean; user: UserProfile }>(
      '/api/auth/check/'
    );
    return response.data.user;
  },

  // Get current user profile
  async getProfile(): Promise<UserProfile> {
    const response = await apiClient.get<UserProfile>('/api/auth/profile/');
    return response.data;
  },

  // Update profile
  async updateProfile(data: UpdateProfileData): Promise<UserProfile> {
    const response = await apiClient.patch<UserProfile>('/api/auth/profile/', data);
    
    // Update user cookie
    Cookies.set('user', JSON.stringify(response.data), { expires: 7 });
    
    return response.data;
  },

  // Change password
  async changePassword(data: ChangePasswordData): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>(
      '/api/auth/change-password/',
      data
    );
    return response.data;
  },

  // Get user from cookie
  getUserFromCookie(): UserProfile | null {
    const userStr = Cookies.get('user');
    if (!userStr) return null;
    
    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  },

  // Check if user is authenticated
  isAuthenticated(): boolean {
    return !!Cookies.get('access_token');
  },
};