'use client';

import { useState, useEffect } from 'react';
import Modal from '@/components/ui/Modal';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import { uploadService, DataUpload, UploadRecord } from '@/services/upload.service';
import { CheckCircle, XCircle, ChevronLeft, ChevronRight } from 'lucide-react';

interface UploadDetailsModalProps {
  isOpen: boolean;
  onClose: () => void;
  upload: DataUpload | null;
}

export default function UploadDetailsModal({ isOpen, onClose, upload }: UploadDetailsModalProps) {
  const [records, setRecords] = useState<UploadRecord[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [filter, setFilter] = useState<'all' | 'valid' | 'invalid'>('all');
  const [page, setPage] = useState(1);
  const [totalRecords, setTotalRecords] = useState(0);
  const pageSize = 20;

  useEffect(() => {
    if (isOpen && upload) {
      fetchRecords();
    }
  }, [isOpen, upload, filter, page]);

  const fetchRecords = async () => {
    if (!upload) return;

    setIsLoading(true);
    try {
      const validOnly = filter === 'valid' ? true : filter === 'invalid' ? false : undefined;
      
      const response = await uploadService.getUploadRecords(upload.id, {
        valid_only: validOnly,
        page,
        page_size: pageSize,
      });

      setRecords(response.results);
      setTotalRecords(response.count);
    } catch (error) {
      console.error('Failed to fetch records:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFilterChange = (newFilter: 'all' | 'valid' | 'invalid') => {
    setFilter(newFilter);
    setPage(1); // Reset to first page
  };

  const totalPages = Math.ceil(totalRecords / pageSize);

  if (!upload) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={`Upload Details: ${upload.file_name}`} size="xl">
      <div className="space-y-4">
        {/* Summary */}
        <div className="grid grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg">
          <div>
            <p className="text-sm text-gray-600">Total Rows</p>
            <p className="text-xl font-bold text-gray-900">{upload.total_rows}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Valid Records</p>
            <p className="text-xl font-bold text-success-600">{upload.processed_rows}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Invalid Records</p>
            <p className="text-xl font-bold text-danger-600">{upload.error_rows}</p>
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="flex space-x-2 border-b border-gray-200">
          <button
            onClick={() => handleFilterChange('all')}
            className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
              filter === 'all'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            All Records ({upload.total_rows})
          </button>
          <button
            onClick={() => handleFilterChange('valid')}
            className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
              filter === 'valid'
                ? 'border-success-600 text-success-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            Valid ({upload.processed_rows})
          </button>
          <button
            onClick={() => handleFilterChange('invalid')}
            className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
              filter === 'invalid'
                ? 'border-danger-600 text-danger-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            Invalid ({upload.error_rows})
          </button>
        </div>

        {/* Records Table */}
        <div className="max-h-[400px] overflow-y-auto">
          {isLoading ? (
            <div className="text-center py-12 text-gray-500">Loading records...</div>
          ) : records.length === 0 ? (
            <div className="text-center py-12 text-gray-500">No records found</div>
          ) : (
            <table className="w-full">
              <thead className="bg-gray-50 sticky top-0">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                    Row #
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                    Status
                  </th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                    Data
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {records.map((record) => (
                  <tr key={record.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">
                      {record.row_number}
                    </td>
                    <td className="px-4 py-3">
                      {record.is_valid ? (
                        <Badge variant="success">
                          <CheckCircle className="w-3 h-3 mr-1 inline" />
                          Valid
                        </Badge>
                      ) : (
                        <Badge variant="danger">
                          <XCircle className="w-3 h-3 mr-1 inline" />
                          Invalid
                        </Badge>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <div className="space-y-1">
                        {/* Show data fields */}
                        <div className="text-xs text-gray-600">
                          {Object.entries(record.data).slice(0, 3).map(([key, value]) => (
                            <span key={key} className="mr-3">
                              <strong>{key}:</strong> {String(value)}
                            </span>
                          ))}
                          {Object.keys(record.data).length > 3 && (
                            <span className="text-gray-400">
                              +{Object.keys(record.data).length - 3} more
                            </span>
                          )}
                        </div>
                        {/* Show errors if invalid */}
                        {!record.is_valid && record.validation_errors.length > 0 && (
                          <div className="text-xs text-danger-600">
                            Errors: {record.validation_errors.join(', ')}
                          </div>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between border-t border-gray-200 pt-4">
            <div className="text-sm text-gray-600">
              Showing {(page - 1) * pageSize + 1} to {Math.min(page * pageSize, totalRecords)} of{' '}
              {totalRecords} records
            </div>
            <div className="flex space-x-2">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setPage(page - 1)}
                disabled={page === 1}
              >
                <ChevronLeft className="w-4 h-4" />
              </Button>
              <span className="px-4 py-2 text-sm text-gray-700">
                Page {page} of {totalPages}
              </span>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setPage(page + 1)}
                disabled={page === totalPages}
              >
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="flex justify-end pt-4 border-t border-gray-200">
          <Button variant="secondary" onClick={onClose}>
            Close
          </Button>
        </div>
      </div>
    </Modal>
  );
}