'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/contexts/ToastContext';
import { auditService, AuditLog } from '@/services/audit.service';
import DashboardLayout from '@/components/layout/DashboardLayout';
import Card, { CardHeader, CardBody } from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import { Activity, User, FileText, Upload, Trash2, Edit, XCircle, Search } from 'lucide-react';
import { formatDistance } from 'date-fns';

export default function ActivityLogsPage() {
  const { user } = useAuth();
  const { showToast } = useToast();
  
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [actionFilter, setActionFilter] = useState('');

  useEffect(() => {
    fetchLogs();
  }, [actionFilter]);

  const fetchLogs = async () => {
    setIsLoading(true);
    try {
      const response = await auditService.getLogs({
        action: actionFilter || undefined,
        search: searchQuery || undefined,
      });
      setLogs(response.results);
    } catch (error) {
      console.error('Failed to fetch logs:', error);
      showToast('error', 'Failed to load activity logs');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = () => {
    fetchLogs();
  };

  const getActionIcon = (action: string) => {
    const icons: Record<string, any> = {
      CREATE: Edit,
      UPDATE: Edit,
      DELETE: Trash2,
      UPLOAD: Upload,
      LOGIN: User,
      LOGOUT: User,
    };
    return icons[action] || Activity;
  };

  const getActionBadge = (action: string) => {
    const variants: Record<string, any> = {
      CREATE: 'success',
      UPDATE: 'info',
      DELETE: 'danger',
      UPLOAD: 'warning',
      LOGIN: 'info',
      LOGOUT: 'default',
    };
    return variants[action] || 'default';
  };

  if (!user?.permissions.can_view_audit_logs) {
    return (
      <DashboardLayout>
        <div className="text-center py-12">
          <XCircle className="w-16 h-16 text-danger-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900">Access Denied</h2>
          <p className="text-gray-600 mt-2">You don't have permission to view activity logs.</p>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Activity Logs</h1>
          <p className="text-gray-600 mt-1">View all system activity and changes</p>
        </div>

        {/* Filters */}
        <Card>
          <CardBody>
            <div className="flex flex-col md:flex-row gap-4">
              {/* Search */}
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search logs..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
              </div>

              {/* Action Filter */}
              <select
                value={actionFilter}
                onChange={(e) => setActionFilter(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">All Actions</option>
                <option value="CREATE">Create</option>
                <option value="UPDATE">Update</option>
                <option value="DELETE">Delete</option>
                <option value="UPLOAD">Upload</option>
                <option value="LOGIN">Login</option>
                <option value="LOGOUT">Logout</option>
              </select>
            </div>
          </CardBody>
        </Card>

        {/* Activity Timeline */}
        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold text-gray-900">Activity Timeline</h2>
          </CardHeader>
          <CardBody className="p-0">
            <div className="max-h-[600px] overflow-y-auto">
              {isLoading ? (
                <div className="text-center py-12 text-gray-500">Loading activity logs...</div>
              ) : logs.length === 0 ? (
                <div className="text-center py-12 text-gray-500">No activity logs found</div>
              ) : (
                <div className="divide-y divide-gray-200">
                  {logs.map((log) => {
                    const ActionIcon = getActionIcon(log.action);
                    return (
                      <div key={log.id} className="px-6 py-4 hover:bg-gray-50">
                        <div className="flex items-start space-x-4">
                          {/* Icon */}
                          <div className={`
                            w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0
                            ${log.action === 'DELETE' ? 'bg-danger-100' :
                              log.action === 'CREATE' ? 'bg-success-100' :
                              log.action === 'UPLOAD' ? 'bg-warning-100' :
                              'bg-primary-100'}
                          `}>
                            <ActionIcon className={`w-5 h-5 ${
                              log.action === 'DELETE' ? 'text-danger-600' :
                              log.action === 'CREATE' ? 'text-success-600' :
                              log.action === 'UPLOAD' ? 'text-warning-600' :
                              'text-primary-600'
                            }`} />
                          </div>

                          {/* Content */}
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center space-x-2">
                                <p className="text-sm font-medium text-gray-900">
                                  {log.user?.username || 'System'}
                                </p>
                                <Badge variant={getActionBadge(log.action)}>
                                  {log.action}
                                </Badge>
                              </div>
                              <p className="text-sm text-gray-500">
                                {formatDistance(new Date(log.timestamp), new Date(), { addSuffix: true })}
                              </p>
                            </div>

                            <p className="text-sm text-gray-700 mt-1">{log.description}</p>

                            {log.entity_repr && (
                              <p className="text-xs text-gray-500 mt-1">
                                <span className="font-medium">{log.entity_type}:</span> {log.entity_repr}
                              </p>
                            )}

                            {/* Show changes if available */}
                            {log.changes && Object.keys(log.changes).length > 0 && (
                              <div className="mt-2 p-2 bg-gray-50 rounded text-xs">
                                <p className="font-medium text-gray-700 mb-1">Changes:</p>
                                {Object.entries(log.changes).map(([field, values]: [string, any]) => (
                                  <div key={field} className="text-gray-600">
                                    <span className="font-medium">{field}:</span>{' '}
                                    {values.old !== undefined && (
                                      <>
                                        <span className="line-through">{String(values.old)}</span>
                                        {' → '}
                                      </>
                                    )}
                                    <span className="text-gray-900">{String(values.new)}</span>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </CardBody>
        </Card>
      </div>
    </DashboardLayout>
  );
}