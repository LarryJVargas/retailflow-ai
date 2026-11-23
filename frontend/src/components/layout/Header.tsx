import React from 'react';
import { Download, Plus, RefreshCw } from 'lucide-react';
import { Button } from '../common/Button';

interface HeaderProps {
  title: string;
  subtitle?: string;
  onDownloadReport: () => void;
  onOpenCreateModal: () => void;
  onRefresh: () => void;
  isDownloadingReport: boolean;
  isRefreshing: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  title,
  subtitle,
  onDownloadReport,
  onOpenCreateModal,
  onRefresh,
  isDownloadingReport,
  isRefreshing,
}) => {
  return (
    <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between shrink-0 shadow-sm">
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">{title}</h1>
        {subtitle && <p className="text-xs text-slate-500">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-2.5">
        <Button
          variant="outline"
          size="sm"
          onClick={onRefresh}
          loading={isRefreshing}
          icon={<RefreshCw className="w-3.5 h-3.5" />}
          title="Actualizar datos"
        >
          Refrescar
        </Button>

        <Button
          variant="outline"
          size="sm"
          onClick={onDownloadReport}
          loading={isDownloadingReport}
          icon={<Download className="w-3.5 h-3.5 text-slate-600" />}
        >
          Descargar CSV
        </Button>

        <Button
          variant="primary"
          size="sm"
          onClick={onOpenCreateModal}
          icon={<Plus className="w-4 h-4" />}
        >
          Nuevo Producto
        </Button>
      </div>
    </header>
  );
};
