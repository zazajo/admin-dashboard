import apiClient from '@/lib/api';

export interface UploadStats {
  total_uploads: number;
  completed_uploads: number;
  failed_uploads: number;
  pending_uploads: number;
  total_records_processed: number;
  total_errors: number;
}

export interface DataUpload {
  id: number;
  file_name: string;
  file_size: number;
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
  total_rows: number;
  processed_rows: number;
  error_rows: number;
  error_message?: string;
  error_details?: any;
  success_rate: number;
  uploaded_by: number;
  uploaded_by_name: string;
  uploaded_by_email: string;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  supporting_documents: any[];
  file_url?: string;
}

export interface UploadRecord {
  id: number;
  row_number: number;
  data: Record<string, any>;
  is_valid: boolean;
  validation_errors: string[];
  created_at: string;
  updated_at: string;
}

export interface PreviewData {
  file_name: string;
  total_rows: number;
  total_columns: number;
  columns: {
    name: string;
    type: string;
    non_null_count: number;
    null_count: number;
    unique_count: number;
    sample_values: string[];
  }[];
  preview_data: Record<string, any>[];
}

export const uploadService = {
  // Get upload statistics
  async getStats(): Promise<UploadStats> {
    const response = await apiClient.get<UploadStats>('/api/uploads/stats/');
    return response.data;
  },

  // Get all uploads
  async getUploads(params?: {
    status?: string;
    search?: string;
    ordering?: string;
  }): Promise<{ count: number; results: DataUpload[] }> {
    const response = await apiClient.get('/api/uploads/', { params });
    return response.data;
  },

  // Get single upload
  async getUpload(id: number): Promise<DataUpload> {
    const response = await apiClient.get<DataUpload>(`/api/uploads/${id}/`);
    return response.data;
  },

  // Preview file before uploading
  async previewFile(file: File): Promise<PreviewData> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<PreviewData>('/api/uploads/preview/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Upload file
  async uploadFile(file: File, supportingDocs?: File[]): Promise<DataUpload> {
    const formData = new FormData();
    formData.append('file', file);

    if (supportingDocs && supportingDocs.length > 0) {
      supportingDocs.forEach((doc) => {
        formData.append('supporting_documents', doc);
      });
    }

    const response = await apiClient.post<DataUpload>('/api/uploads/create/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Process upload
  async processUpload(id: number): Promise<DataUpload> {
    const response = await apiClient.post<DataUpload>(`/api/uploads/${id}/process/`);
    return response.data;
  },

  // Get upload records
  async getUploadRecords(
    id: number,
    params?: {
      valid_only?: boolean;
      page?: number;
      page_size?: number;
    }
  ): Promise<{ count: number; results: UploadRecord[] }> {
    const response = await apiClient.get(`/api/uploads/${id}/records/`, { params });
    return response.data;
  },

  // Delete upload
  async deleteUpload(id: number): Promise<void> {
    await apiClient.delete(`/api/uploads/${id}/delete/`);
  },
};