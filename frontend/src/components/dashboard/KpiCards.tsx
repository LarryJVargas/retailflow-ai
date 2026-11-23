import React from 'react';
import { Package, CheckCircle2, AlertTriangle, XCircle } from 'lucide-react';
import { InventorySummary } from '../../types/inventory';

interface KpiCardsProps {
  summary: InventorySummary | null;
  loading: boolean;
}

export const KpiCards: React.FC<KpiCardsProps> = ({ summary, loading }) => {
  if (loading || !summary) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-28 bg-white border border-slate-200 rounded-xl p-5 animate-pulse flex flex-col justify-between">
            <div className="h-4 bg-slate-200 rounded w-24"></div>
            <div className="h-8 bg-slate-200 rounded w-16"></div>
          </div>
        ))}
      </div>
    );
  }

  const { total_products, healthy_products, low_stock_products, out_of_stock_products } = summary;

  const healthyPercent = total_products > 0 ? Math.round((healthy_products / total_products) * 100) : 0;
  const criticalCount = low_stock_products + out_of_stock_products;

  const cards = [
    {
      title: 'Total en Catálogo',
      value: total_products,
      desc: 'Productos registrados',
      icon: <Package className="w-6 h-6 text-retail-700" />,
      bgIcon: 'bg-retail-50',
      border: 'border-slate-200',
    },
    {
      title: 'Stock Saludable',
      value: healthy_products,
      desc: `${healthyPercent}% del inventario en orden`,
      icon: <CheckCircle2 className="w-6 h-6 text-emerald-600" />,
      bgIcon: 'bg-emerald-50',
      border: 'border-emerald-200/80',
    },
    {
      title: 'Stock Bajo',
      value: low_stock_products,
      desc: 'Existencia por debajo del mínimo',
      icon: <AlertTriangle className="w-6 h-6 text-amber-600" />,
      bgIcon: 'bg-amber-50',
      border: 'border-amber-200/80',
    },
    {
      title: 'Agotados (Stock 0)',
      value: out_of_stock_products,
      desc: 'Quiebre total de góndola',
      icon: <XCircle className="w-6 h-6 text-rose-600" />,
      bgIcon: 'bg-rose-50',
      border: 'border-rose-200/80',
    },
  ];

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {cards.map((c, i) => (
          <div
            key={i}
            className={`bg-white border rounded-xl p-5 shadow-sm transition-all hover:shadow-md ${c.border}`}
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                {c.title}
              </span>
              <div className={`p-2 rounded-lg ${c.bgIcon}`}>{c.icon}</div>
            </div>
            <div className="text-3xl font-extrabold text-slate-900 tracking-tight mb-1">
              {c.value}
            </div>
            <p className="text-xs text-slate-500">{c.desc}</p>
          </div>
        ))}
      </div>

      {criticalCount > 0 && (
        <div className="bg-rose-50 border border-rose-200 rounded-xl p-4 flex items-center justify-between text-rose-900 text-sm">
          <div className="flex items-center gap-2.5">
            <AlertTriangle className="w-5 h-5 text-rose-600 shrink-0" />
            <span>
              <strong>Alerta Operativa:</strong> Existen <strong>{criticalCount} productos</strong> con necesidad de reaprovisionamiento ({out_of_stock_products} agotados y {low_stock_products} con bajo stock).
            </span>
          </div>
        </div>
      )}
    </div>
  );
};
