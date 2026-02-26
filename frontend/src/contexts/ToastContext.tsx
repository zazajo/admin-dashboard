'use client';

import React, { createContext, useContext, useState, useCallback } from 'react';
import { CheckCircle, XCircle, AlertCircle, X } from 'lucide-react';

type ToastType = 'success' | 'error' | 'warning' | 'info';

interface Toast {
  id: string;
  type: ToastType;
  message: string;
}

interface ToastContextType {
  showToast: (type: ToastType, message: string) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const showToast = useCallback((type: ToastType, message: string) => {
    const id = Date.now().toString();
    setToasts((prev) => [...prev, { id, type, message }]);

    // Auto remove after 5 seconds
    setTimeout(() => {
      setToasts((prev) => prev.filter((toast) => toast.id !== id));
    }, 5000);
  }, []);

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  };

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within ToastProvider');
  }
  return context;
}

function ToastContainer({
    toasts,
    onRemove,
  }: {
    toasts: Toast[];
    onRemove: (id: string) => void;
  }) {
    if (toasts.length === 0) return null;
  
    return (
      <div 
        className="fixed top-4 right-4 space-y-2"
        style={{
          zIndex: 99999,
          position: 'fixed',
          top: '1rem',
          right: '1rem',
        }}
      >
        {toasts.map((toast) => (
          <ToastItem key={toast.id} toast={toast} onRemove={onRemove} />
        ))}
      </div>
    );
  }

  function ToastItem({ toast, onRemove }: { toast: Toast; onRemove: (id: string) => void }) {
    const configs = {
      success: {
        bg: 'bg-success-50',
        border: 'border-success-300',
        icon: <CheckCircle className="w-5 h-5 text-success-600" />,
        text: 'text-success-900'
      },
      error: {
        bg: 'bg-danger-50',
        border: 'border-danger-300',
        icon: <XCircle className="w-5 h-5 text-danger-600" />,
        text: 'text-danger-900'
      },
      warning: {
        bg: 'bg-warning-50',
        border: 'border-warning-300',
        icon: <AlertCircle className="w-5 h-5 text-warning-600" />,
        text: 'text-warning-900'
      },
      info: {
        bg: 'bg-primary-50',
        border: 'border-primary-300',
        icon: <AlertCircle className="w-5 h-5 text-primary-600" />,
        text: 'text-primary-900'
      },
    };
  
    const config = configs[toast.type];
  
    return (
      <div
        className={`flex items-center space-x-3 px-4 py-3 rounded-lg border-2 shadow-lg min-w-[300px] max-w-md animate-slide-up ${config.bg} ${config.border}`}
        style={{ zIndex: 9999 }}
      >
        {config.icon}
        <p className={`flex-1 text-sm font-medium ${config.text}`}>
          {toast.message}
        </p>
        <button
          onClick={() => onRemove(toast.id)}
          className="text-gray-500 hover:text-gray-700 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    );
  }