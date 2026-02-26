import apiClient from '@/lib/api';

export interface AuditLog {
  id: number;
  user: {
    id: number;
    username: string;
    email: string;
  } | null;
  action: string;
  entity_type: string;
  entity_id: string;
  entity_repr: string;
  description: string;
  changes: Record<string, any>;
  metadata: Record<string, any>;
  timestamp: string;
}

export const auditService = {
  // Get all audit logs
  async getLogs(params?: {
    action?: string;
    user?: number;
    entity_type?: string;
    search?: string;
    ordering?: string;
    page?: number;
  }): Promise<{ count: number; results: AuditLog[] }> {
    const response = await apiClient.get('/api/audit/logs/', { params });
    return response.data;
  },

  // Get audit log statistics
  async getStats(): Promise<{
    total_logs: number;
    recent_actions: number;
    unique_users: number;
    actions_today: number;
  }> {
    const response = await apiClient.get('/api/audit/stats/');
    return response.data;
  },
};