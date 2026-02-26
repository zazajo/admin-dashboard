'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { userService } from '@/services/user.service';
import DashboardLayout from '@/components/layout/DashboardLayout';
import StatCard from '@/components/dashboard/StatCard';
import Card, { CardHeader, CardBody } from '@/components/ui/Card';
import Badge, { getRoleBadgeVariant } from '@/components/ui/Badge';
import { Users, UserCheck, UserX, Shield, Briefcase, Eye } from 'lucide-react';
import type { UserStats } from '@/types';

export default function DashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState<UserStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      if (user?.permissions.can_manage_users) {
        try {
          const data = await userService.getUserStats();
          setStats(data);
        } catch (error) {
          console.error('Failed to fetch stats:', error);
        }
      }
      setIsLoading(false);
    };

    fetchStats();
  }, [user]);

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Welcome back, {user?.first_name || user?.username}!
          </h1>
          <p className="text-gray-600 mt-1">
            Here's what's happening with your dashboard today.
          </p>
        </div>

        {/* Stats Grid - Only for Admins */}
        {user?.permissions.can_manage_users && stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <StatCard
              title="Total Users"
              value={stats.total_users}
              icon={Users}
              color="blue"
            />
            <StatCard
              title="Active Users"
              value={stats.active_users}
              icon={UserCheck}
              color="green"
            />
            <StatCard
              title="Inactive Users"
              value={stats.inactive_users}
              icon={UserX}
              color="red"
            />
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* User Role Distribution - Only for Admins */}
          {user?.permissions.can_manage_users && stats && (
            <Card>
              <CardHeader>
                <h2 className="text-lg font-semibold text-gray-900">User Distribution</h2>
              </CardHeader>
              <CardBody>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-danger-50 rounded-lg flex items-center justify-center">
                        <Shield className="w-5 h-5 text-danger-600" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">Admins</p>
                        <p className="text-sm text-gray-600">Full system access</p>
                      </div>
                    </div>
                    <span className="text-2xl font-bold text-gray-900">{stats.admins}</span>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-warning-50 rounded-lg flex items-center justify-center">
                        <Briefcase className="w-5 h-5 text-warning-600" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">Managers</p>
                        <p className="text-sm text-gray-600">Can upload & edit data</p>
                      </div>
                    </div>
                    <span className="text-2xl font-bold text-gray-900">{stats.managers}</span>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-primary-50 rounded-lg flex items-center justify-center">
                        <Eye className="w-5 h-5 text-primary-600" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">Viewers</p>
                        <p className="text-sm text-gray-600">Read-only access</p>
                      </div>
                    </div>
                    <span className="text-2xl font-bold text-gray-900">{stats.viewers}</span>
                  </div>
                </div>
              </CardBody>
            </Card>
          )}

          {/* Your Permissions */}
          <Card>
            <CardHeader>
              <h2 className="text-lg font-semibold text-gray-900">Your Permissions</h2>
            </CardHeader>
            <CardBody>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Role</span>
                  <Badge variant={getRoleBadgeVariant(user?.role || '')}>
                    {user?.role}
                  </Badge>
                </div>
                <div className="border-t border-gray-200 pt-3 space-y-2">
                  {Object.entries(user?.permissions || {}).map(([key, value]) => (
                    <div key={key} className="flex items-center justify-between">
                      <span className="text-sm text-gray-600 capitalize">
                        {key.replace('can_', '').replace(/_/g, ' ')}
                      </span>
                      <span className={`text-sm font-medium ${value ? 'text-success-600' : 'text-gray-400'}`}>
                        {value ? '✓ Allowed' : '✗ Denied'}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </CardBody>
          </Card>
        </div>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold text-gray-900">Quick Actions</h2>
          </CardHeader>
          <CardBody>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {user?.permissions.can_manage_users && (
                <a
                  href="/dashboard/users"
                  className="p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors"
                >
                  <Users className="w-6 h-6 text-primary-600 mb-2" />
                  <h3 className="font-medium text-gray-900">Manage Users</h3>
                  <p className="text-sm text-gray-600 mt-1">View and manage all users</p>
                </a>
              )}
              {user?.permissions.can_upload_data && (
                <a
                  href="/dashboard/uploads"
                  className="p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors"
                >
                  <Shield className="w-6 h-6 text-primary-600 mb-2" />
                  <h3 className="font-medium text-gray-900">Upload Data</h3>
                  <p className="text-sm text-gray-600 mt-1">Upload CSV or Excel files</p>
                </a>
              )}
              <a
                href="/dashboard/settings"
                className="p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors"
              >
                <Eye className="w-6 h-6 text-primary-600 mb-2" />
                <h3 className="font-medium text-gray-900">Settings</h3>
                <p className="text-sm text-gray-600 mt-1">Update your profile</p>
              </a>
            </div>
          </CardBody>
        </Card>
      </div>
    </DashboardLayout>
  );
}