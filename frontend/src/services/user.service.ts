import apiClient from '@/lib/api';
import { User, UserStats, RegisterData, PaginatedResponse } from '@/types';

export const userService = {
  // Get all users with optional filters
  async getUsers(params?: {
    search?: string;
    role?: string;
    is_active?: boolean;
    ordering?: string;
    page?: number;
  }): Promise<PaginatedResponse<User>> {
    const response = await apiClient.get<PaginatedResponse<User>>('/api/auth/users/', {
      params,
    });
    return response.data;
  },

  // Get user statistics
  async getUserStats(): Promise<UserStats> {
    const response = await apiClient.get<UserStats>('/api/auth/users/stats/');
    return response.data;
  },

  // Get single user
  async getUser(id: number): Promise<User> {
    const response = await apiClient.get<User>(`/api/auth/users/${id}/`);
    return response.data;
  },

  // Create user
  async createUser(data: RegisterData): Promise<User> {
    const response = await apiClient.post<User>('/api/auth/users/create/', data);
    return response.data;
  },

  // Update user
  async updateUser(
    id: number,
    data: Partial<{
      email: string;
      first_name: string;
      last_name: string;
      role: string;
      is_active: boolean;
    }>
  ): Promise<User> {
    const response = await apiClient.patch<User>(`/api/auth/users/${id}/update/`, data);
    return response.data;
  },

  // Deactivate user (soft delete)
  async deactivateUser(id: number): Promise<void> {
    await apiClient.delete(`/api/auth/users/${id}/delete/`);
  },

  // Activate user
  async activateUser(id: number): Promise<User> {
    const response = await apiClient.post<User>(`/api/auth/users/${id}/activate/`);
    return response.data;
  },
};