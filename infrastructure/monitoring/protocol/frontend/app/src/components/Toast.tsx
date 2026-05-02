import React from 'react';
import { X, Check, AlertCircle } from 'lucide-react';
import type { Toast as ToastType } from '../hooks/useToast';

interface ToastProps {
  toasts: ToastType[];
  onRemove: (id: number) => void;
}

const Toast: React.FC<ToastProps> = ({ toasts, onRemove }) => {
  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
      {toasts.map(toast => (
        <div
          key={toast.id}
          className="animate-slide-in-right flex items-center gap-3 px-5 py-4 rounded-xl shadow-lg min-w-[280px]"
          style={{
            backgroundColor: 'var(--bg-secondary)',
            border: '1px solid var(--border-color)',
            borderLeft: `3px solid ${toast.type === 'success' ? 'var(--success)' : 'var(--danger)'}`,
            boxShadow: '0 4px 16px rgba(0,0,0,0.08)',
          }}
        >
          {toast.type === 'success' ? (
            <Check size={18} style={{ color: 'var(--success)' }} className="flex-shrink-0" />
          ) : (
            <AlertCircle size={18} style={{ color: 'var(--danger)' }} className="flex-shrink-0" />
          )}
          <span className="text-sm flex-1" style={{ color: 'var(--text-primary)' }}>
            {toast.message}
          </span>
          <button
            onClick={() => onRemove(toast.id)}
            className="flex-shrink-0 p-0.5 rounded transition-colors duration-150"
            style={{ color: 'var(--text-tertiary)' }}
            onMouseEnter={e => {
              e.currentTarget.style.color = 'var(--text-secondary)';
              e.currentTarget.style.backgroundColor = 'var(--bg-tertiary)';
            }}
            onMouseLeave={e => {
              e.currentTarget.style.color = 'var(--text-tertiary)';
              e.currentTarget.style.backgroundColor = 'transparent';
            }}
          >
            <X size={14} />
          </button>
        </div>
      ))}
    </div>
  );
};

export default Toast;
