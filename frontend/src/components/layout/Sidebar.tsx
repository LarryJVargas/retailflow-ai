import React, { useEffect } from 'react';
import {
  LayoutDashboard,
  Package,
  AlertTriangle,
  Sparkles,
  Layers,
  X,
} from 'lucide-react';

export type NavigationTab = 'dashboard' | 'products' | 'critical' | 'ai';

interface SidebarProps {
  currentTab: NavigationTab;
  onSelectTab: (tab: NavigationTab) => void;
  criticalCount: number;
  isOpen: boolean;
  onClose: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onSelectTab,
  criticalCount,
  isOpen,
  onClose,
}) => {
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  const navItems: { id: NavigationTab; label: string; icon: React.ReactNode; badge?: number }[] = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: <LayoutDashboard className="w-5 h-5" />,
    },
    {
      id: 'products',
      label: 'Catálogo de Productos',
      icon: <Package className="w-5 h-5" />,
    },
    {
      id: 'critical',
      label: 'Inventario Crítico',
      icon: <AlertTriangle className="w-5 h-5" />,
      badge: criticalCount > 0 ? criticalCount : undefined,
    },
    {
      id: 'ai',
      label: 'Análisis Gemini AI',
      icon: <Sparkles className="w-5 h-5 text-amber-300" />,
    },
  ];

  const handleNavClick = (tab: NavigationTab) => {
    onSelectTab(tab);
    onClose();
  };

  return (
    <>
      {/* Overlay móvil */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/60 backdrop-blur-sm lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      <aside
        aria-label="Menú de navegación"
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-slate-950 text-slate-100 flex flex-col shrink-0 border-r border-slate-800 select-none transform transition-transform duration-200 ease-in-out lg:static lg:translate-x-0 ${
          isOpen ? 'translate-x-0 shadow-2xl' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="h-16 flex items-center justify-between px-5 lg:px-6 border-b border-slate-800/80 gap-3 shrink-0">
          <div className="flex items-center gap-3 min-w-0">
            <div className="w-9 h-9 rounded-lg bg-retail-700 flex items-center justify-center text-white shadow-md shadow-retail-950 shrink-0">
              <Layers className="w-5 h-5" />
            </div>
            <div className="min-w-0">
              <div className="font-bold text-base tracking-tight text-white flex items-center gap-1.5">
                RetailFlow <span className="text-retail-200 text-xs px-1.5 py-0.5 rounded bg-retail-900 border border-retail-700">AI</span>
              </div>
              <div className="text-[11px] text-slate-400 font-medium truncate">Gestión Inteligente</div>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="lg:hidden p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors focus:outline-none focus:ring-2 focus:ring-retail-500"
            aria-label="Cerrar menú de navegación"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Nav Section */}
        <nav className="flex-1 px-3 py-6 space-y-1 overflow-y-auto">
          <div className="px-3 pb-2 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
            Operaciones Retail
          </div>

          {navItems.map((item) => {
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => handleNavClick(item.id)}
                aria-current={isActive ? 'page' : undefined}
                className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all focus:outline-none focus:ring-2 focus:ring-retail-500 ${
                  isActive
                    ? 'bg-retail-700 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-slate-900'
                }`}
              >
                <div className="flex items-center gap-3 min-w-0">
                  <span className="shrink-0">{item.icon}</span>
                  <span className="truncate">{item.label}</span>
                </div>
                {item.badge !== undefined && (
                  <span
                    className={`px-2 py-0.5 text-xs rounded-full font-bold shrink-0 ${
                      isActive
                        ? 'bg-white text-retail-800'
                        : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Footer Info */}
        <div className="p-4 border-t border-slate-800/80 bg-slate-900/40 text-xs text-slate-400 shrink-0">
          <div className="flex items-center justify-between mb-1">
            <span className="font-medium text-slate-300">FastAPI Core</span>
            <span className="flex items-center gap-1 text-emerald-400 text-[11px]">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              Online
            </span>
          </div>
          <div className="text-[11px] text-slate-400">
            RetailFlow AI v0.1.0 • Core Suite
          </div>
        </div>
      </aside>
    </>
  );
};
