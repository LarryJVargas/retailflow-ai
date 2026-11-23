import React, { useState } from 'react';
import { AlertTriangle, XCircle, ArrowUpRight } from 'lucide-react';
import { InventoryItem } from '../../types/inventory';
import { InventoryStatusBadge } from '../common/Badge';

interface CriticalInventoryViewProps {
  lowStockItems: InventoryItem[];
  outOfStockItems: InventoryItem[];
  loading: boolean;
  onNavigateToAi?: () => void;
}

export const CriticalInventoryView: React.FC<CriticalInventoryViewProps> = ({
  lowStockItems,
  outOfStockItems,
  loading,
  onNavigateToAi,
}) => {
  const [activeTab, setActiveTab] = useState<'all' | 'out' | 'low'>('all');

  const totalCritical = lowStockItems.length + outOfStockItems.length;

  const displayedItems =
    activeTab === 'out'
      ? outOfStockItems
      : activeTab === 'low'
      ? lowStockItems
      : [...outOfStockItems, ...lowStockItems];

  return (
    <div className="space-y-4">
      {/* Banner de llamada de atención hacia Gemini */}
      <div className="bg-gradient-to-r from-slate-900 to-retail-950 text-white rounded-xl p-5 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-retail-700/60 text-retail-100 border border-retail-500/30 mb-2">
            Control de Abastecimiento Retail
          </div>
          <h2 className="text-lg font-bold tracking-tight">
            {totalCritical === 0
              ? 'Inventario en niveles óptimos'
              : `${totalCritical} productos requieren atención urgente`}
          </h2>
          <p className="text-xs text-slate-300 mt-0.5 max-w-xl">
            Los cálculos de reposición se basan en la fórmula matemática determinista del backend:{' '}
            <code className="text-retail-200 font-mono">max(minimum_stock - stock, 0)</code>.
          </p>
        </div>

        {onNavigateToAi && totalCritical > 0 && (
          <button
            onClick={onNavigateToAi}
            className="inline-flex items-center gap-2 px-4 py-2 text-xs font-bold bg-amber-400 hover:bg-amber-300 text-slate-950 rounded-lg transition-colors shrink-0 shadow-sm"
          >
            Priorizar con Gemini AI
            <ArrowUpRight className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Tabs de filtro rápido */}
      <div className="flex items-center gap-2 border-b border-slate-200 pb-2">
        <button
          onClick={() => setActiveTab('all')}
          className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
            activeTab === 'all'
              ? 'bg-retail-700 text-white'
              : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          Todos ({totalCritical})
        </button>
        <button
          onClick={() => setActiveTab('out')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
            activeTab === 'out'
              ? 'bg-rose-600 text-white'
              : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          <XCircle className="w-3.5 h-3.5" />
          Agotados ({outOfStockItems.length})
        </button>
        <button
          onClick={() => setActiveTab('low')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
            activeTab === 'low'
              ? 'bg-amber-600 text-white'
              : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          <AlertTriangle className="w-3.5 h-3.5" />
          Stock Bajo ({lowStockItems.length})
        </button>
      </div>

      {/* Tabla de artículos críticos */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 border-b border-slate-200 text-xs font-semibold uppercase tracking-wider text-slate-500">
              <tr>
                <th className="px-6 py-3">SKU</th>
                <th className="px-6 py-3">Nombre</th>
                <th className="px-6 py-3">Categoría</th>
                <th className="px-6 py-3 text-center">Stock Actual</th>
                <th className="px-6 py-3 text-center">Stock Mínimo</th>
                <th className="px-6 py-3 text-center">Estado</th>
                <th className="px-6 py-3 text-center bg-retail-50/50 text-retail-800">
                  Reposición Sugerida
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                [1, 2, 3].map((i) => (
                  <tr key={i} className="animate-pulse">
                    <td colSpan={7} className="px-6 py-4">
                      <div className="h-5 bg-slate-100 rounded w-full"></div>
                    </td>
                  </tr>
                ))
              ) : displayedItems.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-slate-400">
                    <p className="font-semibold text-slate-600 mb-1">
                      No hay productos críticos en esta categoría
                    </p>
                    <p className="text-xs text-slate-400">
                      Todos los productos seleccionados cuentan con existencias dentro de los márgenes normales.
                    </p>
                  </td>
                </tr>
              ) : (
                displayedItems.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="px-6 py-3.5 font-mono text-xs font-bold text-slate-800 whitespace-nowrap">
                      {item.sku}
                    </td>
                    <td className="px-6 py-3.5 font-medium text-slate-900">
                      {item.name}
                    </td>
                    <td className="px-6 py-3.5 text-slate-600 whitespace-nowrap">
                      <span className="px-2 py-0.5 rounded text-xs bg-slate-100 font-medium">
                        {item.category}
                      </span>
                    </td>
                    <td className="px-6 py-3.5 text-center whitespace-nowrap">
                      <span
                        className={`font-bold text-sm ${
                          item.stock === 0 ? 'text-rose-600' : 'text-amber-600'
                        }`}
                      >
                        {item.stock}
                      </span>
                    </td>
                    <td className="px-6 py-3.5 text-center text-slate-500 font-medium whitespace-nowrap">
                      {item.minimum_stock}
                    </td>
                    <td className="px-6 py-3.5 text-center whitespace-nowrap">
                      <InventoryStatusBadge status={item.status} />
                    </td>
                    <td className="px-6 py-3.5 text-center font-bold text-base text-retail-700 bg-retail-50/30 whitespace-nowrap">
                      +{item.suggested_restock} u.
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
