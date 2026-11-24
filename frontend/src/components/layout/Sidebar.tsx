import React from 'react';
import {
  LayoutDashboard,
  Package,
  AlertTriangle,
  Sparkles,
  Layers,
} from 'lucide-react';

export type NavigationTab = 'dashboard' | 'products' | 'critical' | 'ai';

interface SidebarProps {
  currentTab: NavigationTab;
  onSelectTab: (tab: NavigationTab) => void;
  criticalCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onSelectTab,
  criticalCount,
}) => {
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

  return (
    <aside className="w-64 bg-slate-950 text-slate-100 flex flex-col shrink-0 border-r border-slate-800 select-none">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 border-b border-slate-800/80 gap-3">
        <div className="w-9 h-9 rounded-lg bg-retail-700 flex items-center justify-center text-white shadow-md shadow-retail-950">
          <Layers className="w-5 h-5" />
        </div>
        <div>
          <div className="font-bold text-base tracking-tight text-white flex items-center gap-1.5">
            RetailFlow <span className="text-retail-200 text-xs px-1.5 py-0.5 rounded bg-retail-900 border border-retail-700">AI</span>
          </div>
          <div className="text-[11px] text-slate-400 font-medium">Gestión Inteligente</div>
        </div>
      </div>

      {/* Nav Section */}
      <div className="flex-1 px-3 py-6 space-y-1">
        <div className="px-3 pb-2 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
          Operaciones Retail
        </div>

        {navItems.map((item) => {
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-retail-700 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-100 hover:bg-slate-900'
              }`}
            >
              <div className="flex items-center gap-3">
                {item.icon}
                <span>{item.label}</span>
              </div>
              {item.badge !== undefined && (
                <span
                  className={`px-2 py-0.5 text-xs rounded-full font-bold ${
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
      </div>

      {/* Footer Info */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-900/40 text-xs text-slate-400">
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
  );
};
