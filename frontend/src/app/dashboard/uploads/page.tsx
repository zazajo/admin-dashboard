'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/contexts/ToastContext';
import { uploadService, DataUpload, UploadStats } from '@/services/upload.service';
import DashboardLayout from '@/components/layout/DashboardLayout';
import Card, { CardHeader, CardBody } from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import FileUpload from '@/components/uploads/FileUpload';
import UploadDetailsModal from '@/components/uploads/UploadDetailsModal';
import { Upload, FileSpreadsheet, CheckCircle, XCircle, Clock, AlertCircle, Eye, Trash2 } from 'lucide-react';
import { formatDistance } from 'date-fns';

export default function UploadsPage() {
  const { user } = useAuth();
  const { showToast } = useToast();
  
  const [stats, setStats] = useState<UploadStats | null>(null);
  const [uploads, setUploads] = useState<DataUpload[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [selectedUpload, setSelectedUpload] = useState<DataUpload | null>(null);
  const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false);

  useEffect(() => {
    fetchData();
  }, [statusFilter]);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [statsData, uploadsData] = await Promise.all([
        uploadService.getStats(),
        uploadService.getUploads({ status: statusFilter || undefined }),
      ]);
      setStats(statsData);
      setUploads(uploadsData.results);
    } catch (error) {
      console.error('Failed to fetch data:', error);
      showToast('error', 'Failed to load uploads');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileSelect = (files: File[]) => {
    if (files.length > 0) {
      setSelectedFile(files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      showToast('warning', 'Please select a file first');
      return;
    }

    setIsUploading(true);
    try {
      // Upload file
      const upload = await uploadService.uploadFile(selectedFile);
      showToast('success', `File "${selectedFile.name}" uploaded successfully!`);
      
      // Process immediately
      await uploadService.processUpload(upload.id);
      showToast('success', 'File processed successfully!');
      
      // Refresh data
      setSelectedFile(null);
      fetchData();
    } catch (error: any) {
      showToast('error', error.response?.data?.error || 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  const handleViewDetails = (upload: DataUpload) => {
    setSelectedUpload(upload);
    setIsDetailsModalOpen(true);
  };

  const handleDeleteUpload = async (id: number, fileName: string) => {
    if (!confirm(`Are you sure you want to delete "${fileName}"?`)) {
      return;
    }

    try {
      await uploadService.deleteUpload(id);
      showToast('success', 'Upload deleted successfully');
      fetchData();
    } catch (error) {
      showToast('error', 'Failed to delete upload');
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, { variant: any; icon: any; text: string }> = {
      COMPLETED: { variant: 'success', icon: CheckCircle, text: 'Completed' },
      FAILED: { variant: 'danger', icon: XCircle, text: 'Failed' },
      PROCESSING: { variant: 'warning', icon: Clock, text: 'Processing' },
      PENDING: { variant: 'info', icon: AlertCircle, text: 'Pending' },
    };

    const config = variants[status] || variants.PENDING;
    const Icon = config.icon;

    return (
      <Badge variant={config.variant}>
        <Icon className="w-3 h-3 mr-1 inline" />
        {config.text}
      </Badge>
    );
  };

  if (!user?.permissions.can_upload_data) {
    return (
      <DashboardLayout>
        <div className="text-center py-12">
          <XCircle className="w-16 h-16 text-danger-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900">Access Denied</h2>
          <p className="text-gray-600 mt-2">You don't have permission to upload data.</p>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Data Uploads</h1>
          <p className="text-gray-600 mt-1">Upload and manage CSV/Excel files</p>
        </div>

        {/* Statistics */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card hover>
              <CardBody>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Total Uploads</p>
                    <p className="text-2xl font-bold text-gray-900 mt-1">{stats.total_uploads}</p>
                  </div>
                  <div className="w-12 h-12 bg-primary-50 rounded-lg flex items-center justify-center">
                    <FileSpreadsheet className="w-6 h-6 text-primary-600" />
                  </div>
                </div>
              </CardBody>
            </Card>

            <Card hover>
              <CardBody>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Completed</p>
                    <p className="text-2xl font-bold text-gray-900 mt-1">{stats.completed_uploads}</p>
                  </div>
                  <div className="w-12 h-12 bg-success-50 rounded-lg flex items-center justify-center">
                    <CheckCircle className="w-6 h-6 text-success-600" />
                  </div>
                </div>
              </CardBody>
            </Card>

            <Card hover>
              <CardBody>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Records Processed</p>
                    <p className="text-2xl font-bold text-gray-900 mt-1">
                      {stats.total_records_processed.toLocaleString()}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-primary-50 rounded-lg flex items-center justify-center">
                    <Upload className="w-6 h-6 text-primary-600" />
                  </div>
                </div>
              </CardBody>
            </Card>

            <Card hover>
              <CardBody>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Errors</p>
                    <p className="text-2xl font-bold text-gray-900 mt-1">
                      {stats.total_errors.toLocaleString()}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-danger-50 rounded-lg flex items-center justify-center">
                    <XCircle className="w-6 h-6 text-danger-600" />
                  </div>
                </div>
              </CardBody>
            </Card>
          </div>
        )}

        {/* Upload Section */}
        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold text-gray-900">Upload New File</h2>
          </CardHeader>
          <CardBody>
            <FileUpload onFileSelect={handleFileSelect} />
            {selectedFile && (
              <div className="mt-4 flex justify-end">
                <Button
                  onClick={handleUpload}
                  variant="primary"
                  isLoading={isUploading}
                  className="flex items-center space-x-2"
                >
                  <Upload className="w-4 h-4" />
                  <span>Upload & Process</span>
                </Button>
              </div>
            )}
          </CardBody>
        </Card>

        {/* Upload History */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">Upload History</h2>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">All Status</option>
                <option value="COMPLETED">Completed</option>
                <option value="FAILED">Failed</option>
                <option value="PROCESSING">Processing</option>
                <option value="PENDING">Pending</option>
              </select>
            </div>
          </CardHeader>
          <CardBody className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      File Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Records
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Success Rate
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Uploaded
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {isLoading ? (
                    <tr>
                      <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                        Loading uploads...
                      </td>
                    </tr>
                  ) : uploads.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                        No uploads found
                      </td>
                    </tr>
                  ) : (
                    uploads.map((upload) => (
                      <tr key={upload.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4">
                          <div className="flex items-center space-x-3">
                            <FileSpreadsheet className="w-5 h-5 text-primary-600" />
                            <div>
                              <p className="text-sm font-medium text-gray-900">{upload.file_name}</p>
                              <p className="text-xs text-gray-500">
                                {(upload.file_size / 1024).toFixed(2)} KB
                              </p>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4">{getStatusBadge(upload.status)}</td>
                        <td className="px-6 py-4">
                          <div className="text-sm">
                            <p className="text-gray-900">{upload.total_rows} total</p>
                            {upload.status === 'COMPLETED' && (
                              <p className="text-xs text-gray-500">
                                {upload.processed_rows} valid, {upload.error_rows} errors
                              </p>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          {upload.status === 'COMPLETED' && (
                            <div className="flex items-center space-x-2">
                              <div className="w-full bg-gray-200 rounded-full h-2 max-w-[100px]">
                                <div
                                  className={`h-2 rounded-full ${
                                    upload.success_rate >= 80
                                      ? 'bg-success-600'
                                      : upload.success_rate >= 50
                                      ? 'bg-warning-600'
                                      : 'bg-danger-600'
                                  }`}
                                  style={{ width: `${upload.success_rate}%` }}
                                />
                              </div>
                              <span className="text-sm text-gray-600">{upload.success_rate}%</span>
                            </div>
                          )}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500">
                          {formatDistance(new Date(upload.created_at), new Date(), { addSuffix: true })}
                        </td>
                        <td className="px-6 py-4 text-right">
                          <div className="flex items-center justify-end space-x-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleViewDetails(upload)}
                              title="View details"
                            >
                              <Eye className="w-4 h-4" />
                            </Button>
                            {user?.permissions.can_delete_data && (
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleDeleteUpload(upload.id, upload.file_name)}
                                className="text-danger-600 hover:text-danger-700"
                                title="Delete upload"
                              >
                                <Trash2 className="w-4 h-4" />
                              </Button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Upload Details Modal */}
      <UploadDetailsModal
        isOpen={isDetailsModalOpen}
        onClose={() => setIsDetailsModalOpen(false)}
        upload={selectedUpload}
      />
    </DashboardLayout>
  );
}