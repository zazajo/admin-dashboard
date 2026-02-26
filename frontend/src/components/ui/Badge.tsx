import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info';
  className?: string;
}

export default function Badge({ children, variant = 'default', className = '' }: BadgeProps) {
  const variants = {
    default: 'bg-gray-100 text-gray-800',
    success: 'bg-success-50 text-success-700',
    warning: 'bg-warning-50 text-warning-700',
    danger: 'bg-danger-50 text-danger-700',
    info: 'bg-primary-50 text-primary-700',
  };

  return (
    <span
      className={`
        inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
        ${variants[variant]}
        ${className}
      `}
    >
      {children}
    </span>
  );
}

// Helper function to get role badge variant
export function getRoleBadgeVariant(role: string): 'default' | 'success' | 'warning' | 'danger' | 'info' {
  switch (role) {
    case 'ADMIN':
      return 'danger';
    case 'MANAGER':
      return 'warning';
    case 'VIEWER':
      return 'info';
    default:
      return 'default';
  }
}