import React from 'react';
import { InventoryStatus } from '../../types/inventory';
import { PriorityLevel } from '../../types/ai';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'healthy' | 'low' | 'out' | 'critical' | 'high' | 'medium' | 'low-priority' | 'gemini' | 'fallback' | 'default';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ children, variant = 'default', className = '' }) => {
  const variantStyles: Record<string, string> = {
    healthy: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    low: 'bg-amber-50 text-amber-700 border-amber-200',
    out: 'bg-rose-50 text-rose-700 border-rose-200',
    critical: 'bg-rose-100 text-rose-800 border-rose-300 font-semibold',
    high: 'bg-orange-100 text-orange-800 border-orange-300 font-semibold',
    medium: 'bg-amber-100 text-amber-800 border-amber-300',
    'low-priority': 'bg-blue-100 text-blue-800 border-blue-300',
    gemini: 'bg-purple-50 text-purple-700 border-purple-200 font-medium',
    fallback: 'bg-slate-100 text-slate-700 border-slate-300 font-medium',
    default: 'bg-slate-100 text-slate-700 border-slate-200',
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs border ${
        variantStyles[variant] || variantStyles.default
      } ${className}`}
    >
      {children}
    </span>
  );
};

export const InventoryStatusBadge: React.FC<{ status: InventoryStatus }> = ({ status }) => {
  switch (status) {
    case 'HEALTHY':
      return <Badge variant="healthy">Saludable</Badge>;
    case 'LOW_STOCK':
      return <Badge variant="low">Stock Bajo</Badge>;
    case 'OUT_OF_STOCK':
      return <Badge variant="out">Agotado</Badge>;
    default:
      return <Badge>{status}</Badge>;
  }
};

export const PriorityBadge: React.FC<{ priority: PriorityLevel }> = ({ priority }) => {
  switch (priority) {
    case 'CRITICAL':
      return <Badge variant="critical">CRÍTICA</Badge>;
    case 'HIGH':
      return <Badge variant="high">ALTA</Badge>;
    case 'MEDIUM':
      return <Badge variant="medium">MEDIA</Badge>;
    case 'LOW':
      return <Badge variant="low-priority">BAJA</Badge>;
    default:
      return <Badge>{priority}</Badge>;
  }
};
