import React from 'react';
import { AlertCircle, CheckCircle2, Info, X } from 'lucide-react';

export interface NotificationState {
  type: 'success' | 'error' | 'info';
  message: string;
}

interface NotificationProps {
  notification: NotificationState | null;
  onClose: () => void;
}

export const Notification: React.FC<NotificationProps> = ({ notification, onClose }) => {
  if (!notification) return null;

  const styles = {
    success: 'bg-emerald-50 text-emerald-800 border-emerald-200',
    error: 'bg-rose-50 text-rose-800 border-rose-200',
    info: 'bg-blue-50 text-blue-800 border-blue-200',
  };

  const icons = {
    success: <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />,
    error: <AlertCircle className="w-5 h-5 text-rose-600 shrink-0" />,
    info: <Info className="w-5 h-5 text-blue-600 shrink-0" />,
  };

  return (
    <div
      className={`flex items-start gap-3 p-4 rounded-xl border shadow-sm transition-all duration-200 ${
        styles[notification.type]
      }`}
    >
      {icons[notification.type]}
      <div className="flex-1 text-sm font-medium">{notification.message}</div>
      <button
        onClick={onClose}
        className="text-slate-400 hover:text-slate-700 transition-colors p-0.5 rounded"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  );
};
