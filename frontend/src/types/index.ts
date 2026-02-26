// User Types
export type UserRole = 'ADMIN' | 'MANAGER' | 'VIEWER';

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface UserProfile extends User {
  permissions: UserPermissions;
}

export interface UserPermissions {
  can_manage_users: boolean;
  can_upload_data: boolean;
  can_edit_data: boolean;
  can_delete_data: boolean;
  can_export_reports: boolean;
  can_view_audit_logs: boolean;
}

export interface UserStats {
  total_users: number;
  active_users: number;
  inactive_users: number;
  admins: number;
  managers: number;
  viewers: number;
}

// Auth Types
export interface LoginCredentials {
  username: string;
  password: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: UserProfile;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  password_confirm: string;
  first_name: string;
  last_name: string;
  role: UserRole;
}

export interface UpdateProfileData {
  email?: string;
  first_name?: string;
  last_name?: string;
}

export interface ChangePasswordData {
  old_password: string;
  new_password: string;
  new_password_confirm: string;
}

// API Response Types
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ApiError {
  detail?: string;
  [key: string]: any;
}

// Upload Types (for Week 2)
export interface DataUpload {
  id: number;
  file_name: string;
  file_size: number;
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
  total_rows: number;
  processed_rows: number;
  error_rows: number;
  uploaded_by: User;
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

// Audit Log Types (for Week 2)
export interface AuditLog {
  id: number;
  user: User | null;
  action: string;
  entity_type: string;
  entity_id: string;
  entity_repr: string;
  description: string;
  changes: Record<string, any>;
  metadata: Record<string, any>;
  timestamp: string;
}