'use client';

import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/contexts/ToastContext';
import DashboardLayout from '@/components/layout/DashboardLayout';
import Card, { CardHeader, CardBody } from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import { Download, FileText, Users, Upload as UploadIcon, Activity, XCircle } from 'lucide-react';

export default function ReportsPage() {
  const { user } = useAuth();
  const { showToast } = useToast();
  const [isGenerating, setIsGenerating] = useState<string | null>(null);

  const handleGenerateReport = async (reportType: string, format: 'csv' | 'pdf' = 'csv') => {
    setIsGenerating(reportType);
    showToast('info', `Generating ${reportType} report...`);
    
    // Simulate report generation
    setTimeout(() => {
      showToast('success', `${reportType} report generated! Download started.`);
      setIsGenerating(null);
      
      // In a real implementation, you would:
      // 1. Call backend API to generate report
      // 2. Download the file
      // Example:
      // const response = await fetch(`/api/reports/${reportType.toLowerCase()}`);
      // const blob = await response.blob();
      // const url = window.URL.createObjectURL(blob);
      // const a = document.createElement('a');
      // a.href = url;
      // a.download = `${reportType}-${new Date().toISOString()}.${format}`;
      // a.click();
    }, 2000);
  };

  if (!user?.permissions.can_export_reports) {
    return (
      <DashboardLayout>
        <div className="text-center py-12">
          <XCircle className="w-16 h-16 text-danger-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900">Access Denied</h2>
          <p className="text-gray-600 mt-2">You don't have permission to export reports.</p>
        </div>
      </DashboardLayout>
    );
  }

  const reports = [
    {
      id: 'users',
      title: 'Users Report',
      description: 'Export all users data with roles and status',
      icon: Users,
      iconBg: 'bg-primary-100',
      iconColor: 'text-primary-600',
      format: 'csv' as const,
    },
    {
      id: 'uploads',
      title: 'Upload Statistics',
      description: 'Export upload history with success rates',
      icon: UploadIcon,
      iconBg: 'bg-success-100',
      iconColor: 'text-success-600',
      format: 'csv' as const,
    },
    {
      id: 'activity',
      title: 'Activity Logs',
      description: 'Export complete audit trail with timestamps',
      icon: Activity,
      iconBg: 'bg-warning-100',
      iconColor: 'text-warning-600',
      format: 'pdf' as const,
    },
    {
      id: 'summary',
      title: 'System Summary',
      description: 'Comprehensive system overview report',
      icon: FileText,
      iconBg: 'bg-danger-100',
      iconColor: 'text-danger-600',
      format: 'pdf' as const,
    },
  ];

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Reports</h1>
          <p className="text-gray-600 mt-1">Generate and export system reports</p>
        </div>

        {/* Info Banner */}
        <Card>
          <CardBody className="bg-blue-50 border border-blue-200">
            <div className="flex items-start space-x-3">
              <FileText className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-blue-900">Export Reports</p>
                <p className="text-sm text-blue-700 mt-1">
                  Generate detailed reports in CSV or PDF format. Reports include data from all accessible resources based on your permissions.
                </p>
              </div>
            </div>
          </CardBody>
        </Card>

        {/* Reports Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {reports.map((report) => {
            const Icon = report.icon;
            const isLoading = isGenerating === report.id;

            return (
              <Card key={report.id} hover>
                <CardHeader>
                  <div className="flex items-center space-x-3">
                    <div className={`w-12 h-12 ${report.iconBg} rounded-lg flex items-center justify-center`}>
                      <Icon className={`w-6 h-6 ${report.iconColor}`} />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900">{report.title}</h3>
                      <p className="text-sm text-gray-600">{report.description}</p>
                    </div>
                  </div>
                </CardHeader>
                <CardBody>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-500 uppercase font-medium">
                      Format: {report.format.toUpperCase()}
                    </span>
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={() => handleGenerateReport(report.id, report.format)}
                      isLoading={isLoading}
                      disabled={!!isGenerating && !isLoading}
                    >
                      <Download className="w-4 h-4 mr-2" />
                      {isLoading ? 'Generating...' : 'Export'}
                    </Button>
                  </div>
                </CardBody>
              </Card>
            );
          })}
        </div>

        {/* Additional Info */}
        <Card>
          <CardHeader>
            <h3 className="font-semibold text-gray-900">Report Information</h3>
          </CardHeader>
          <CardBody>
            <div className="space-y-3 text-sm text-gray-700">
              <div className="flex items-start space-x-2">
                <span className="font-medium text-gray-900 min-w-[120px]">Users Report:</span>
                <span>Includes username, email, role, status, and last login date</span>
              </div>
              <div className="flex items-start space-x-2">
                <span className="font-medium text-gray-900 min-w-[120px]">Upload Stats:</span>
                <span>File name, upload date, total rows, success rate, and errors</span>
              </div>
              <div className="flex items-start space-x-2">
                <span className="font-medium text-gray-900 min-w-[120px]">Activity Logs:</span>
                <span>All system actions with user, timestamp, and change details</span>
              </div>
              <div className="flex items-start space-x-2">
                <span className="font-medium text-gray-900 min-w-[120px]">System Summary:</span>
                <span>Comprehensive overview with statistics and trends</span>
              </div>
            </div>
          </CardBody>
        </Card>
      </div>
    </DashboardLayout>
  );
}