import React from 'react';
import { Download, Menu, Plus, RefreshCw } from 'lucide-react';
import { Button } from '../common/Button';

interface HeaderProps {
  title: string;
  subtitle?: string;
  onDownloadReport: () => void;
  onOpenCreateModal: () => void;
  onRefresh: () => void;
  onOpenMobileMenu: () => void;
  isMobileMenuOpen: boolean;
  isDownloadingReport: boolean;
  isRefreshing: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  title,
  subtitle,
  onDownloadReport,
  onOpenCreateModal,
  onRefresh,
  onOpenMobileMenu,
  isMobileMenuOpen,
  isDownloadingReport,
  isRefreshing,
}) => {
  return (
    <header className="min-h-16 bg-white border-b border-slate-200 px-4 sm:px-6 py-3 lg:py-0 lg:h-16 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shrink-0 shadow-sm">
      <div className="flex items-start sm:items-center gap-3 min-w-0">
        <button
          type="button"
          onClick={onOpenMobileMenu}
          className="lg:hidden p-2 -ml-1.5 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors shrink-0 focus:outline-none focus:ring-2 focus:ring-retail-600"
          aria-label="Abrir menú de navegación"
          aria-expanded={isMobileMenuOpen}
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="min-w-0">
          <h1 className="text-lg sm:text-xl font-bold text-slate-900 tracking-tight leading-tight break-words">
            {title}
          </h1>
          {subtitle && (
            <p className="text-xs text-slate-500 mt-0.5 leading-snug">{subtitle}</p>
          )}
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2 shrink-0">
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
