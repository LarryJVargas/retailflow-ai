import React, { useState, useMemo } from 'react';
import { Search, Edit3, Trash2, Filter } from 'lucide-react';
import { Product } from '../../types/product';
import { InventoryStatusBadge } from '../common/Badge';

interface ProductTableProps {
  products: Product[];
  loading: boolean;
  onEdit: (product: Product) => void;
  onDelete: (product: Product) => void;
}

export const ProductTable: React.FC<ProductTableProps> = ({
  products,
  loading,
  onEdit,
  onDelete,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState<'ALL' | 'HEALTHY' | 'LOW_STOCK' | 'OUT_OF_STOCK'>('ALL');

  // Categorías únicas
  const categories = useMemo(() => {
    const set = new Set<string>();
    products.forEach((p) => {
      if (p.category) set.add(p.category);
    });
    return Array.from(set).sort();
  }, [products]);

  // Filtrado de productos
  const filteredProducts = useMemo(() => {
    return products.filter((p) => {
      const matchSearch =
        p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.sku.toLowerCase().includes(searchTerm.toLowerCase());

      const matchCategory = !categoryFilter || p.category === categoryFilter;

      let matchStatus = true;
      if (statusFilter === 'OUT_OF_STOCK') {
        matchStatus = p.stock === 0;
      } else if (statusFilter === 'LOW_STOCK') {
        matchStatus = p.stock > 0 && p.stock < p.minimum_stock;
      } else if (statusFilter === 'HEALTHY') {
        matchStatus = p.stock > 0 && p.stock >= p.minimum_stock;
      }

      return matchSearch && matchCategory && matchStatus;
    });
  }, [products, searchTerm, categoryFilter, statusFilter]);

  const getProductStatus = (stock: number, minimum_stock: number) => {
    if (stock === 0) return 'OUT_OF_STOCK';
    if (stock < minimum_stock) return 'LOW_STOCK';
    return 'HEALTHY';
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden flex flex-col">
      {/* Controles de búsqueda y filtros */}
      <div className="p-4 border-b border-slate-100 flex flex-col md:flex-row gap-3 items-stretch md:items-center justify-between bg-slate-50/40">
        <div className="relative w-full md:flex-1 md:max-w-md">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            aria-label="Buscar por nombre o SKU"
            placeholder="Buscar por nombre o SKU..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-sm bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-retail-600 focus:border-transparent transition-all placeholder:text-slate-400"
          />
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <div className="flex items-center gap-1.5 text-xs text-slate-500 font-medium">
            <Filter className="w-3.5 h-3.5" />
            <span>Filtros:</span>
          </div>

          <select
            aria-label="Filtrar por categoría"
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="flex-1 sm:flex-none min-w-[140px] px-3 py-1.5 text-xs bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-retail-600 font-medium text-slate-700"
          >
            <option value="">Todas las categorías</option>
            {categories.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>

          <select
            aria-label="Filtrar por estado de stock"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as 'ALL' | 'HEALTHY' | 'LOW_STOCK' | 'OUT_OF_STOCK')}
            className="flex-1 sm:flex-none min-w-[140px] px-3 py-1.5 text-xs bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-retail-600 font-medium text-slate-700"
          >
            <option value="ALL">Todos los estados</option>
            <option value="HEALTHY">Saludable</option>
            <option value="LOW_STOCK">Stock Bajo</option>
            <option value="OUT_OF_STOCK">Agotado</option>
          </select>
        </div>
      </div>

      {/* Tabla */}
      <div className="overflow-x-auto">
        <table className="w-full min-w-[720px] text-left text-sm">
          <thead className="bg-slate-50 border-b border-slate-200 text-xs font-semibold uppercase tracking-wider text-slate-500">
            <tr>
              <th className="px-4 sm:px-6 py-3">ID / SKU</th>
              <th className="px-4 sm:px-6 py-3">Nombre</th>
              <th className="px-4 sm:px-6 py-3">Categoría</th>
              <th className="px-4 sm:px-6 py-3 text-right">Precio</th>
              <th className="px-4 sm:px-6 py-3 text-center">Stock Actual</th>
              <th className="px-4 sm:px-6 py-3 text-center">Stock Mínimo</th>
              <th className="px-4 sm:px-6 py-3 text-center">Estado</th>
              <th className="px-4 sm:px-6 py-3 text-right">Acciones</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {loading ? (
              [1, 2, 3, 4, 5].map((i) => (
                <tr key={i} className="animate-pulse">
                  <td colSpan={8} className="px-6 py-4">
                    <div className="h-5 bg-slate-100 rounded w-full"></div>
                  </td>
                </tr>
              ))
            ) : filteredProducts.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-6 py-12 text-center text-slate-400">
                  <div className="max-w-sm mx-auto">
                    <p className="font-semibold text-slate-600 mb-1">No se encontraron productos</p>
                    <p className="text-xs text-slate-400">
                      {searchTerm || categoryFilter || statusFilter !== 'ALL'
                        ? 'Prueba modificando los filtros o el término de búsqueda.'
                        : 'El catálogo está vacío. Comienza agregando un producto nuevo.'}
                    </p>
                  </div>
                </td>
              </tr>
            ) : (
              filteredProducts.map((p) => {
                const status = getProductStatus(p.stock, p.minimum_stock);
                return (
                  <tr key={p.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="px-4 sm:px-6 py-3.5 whitespace-nowrap">
                      <div className="font-mono text-xs font-bold text-slate-800">{p.sku}</div>
                      <div className="text-[11px] text-slate-400">#{p.id}</div>
                    </td>
                    <td className="px-4 sm:px-6 py-3.5 font-medium text-slate-900">
                      {p.name}
                    </td>
                    <td className="px-4 sm:px-6 py-3.5 text-slate-600 whitespace-nowrap">
                      <span className="px-2 py-0.5 rounded text-xs bg-slate-100 font-medium">
                        {p.category}
                      </span>
                    </td>
                    <td className="px-4 sm:px-6 py-3.5 text-right font-medium text-slate-900 whitespace-nowrap">
                      ${p.price.toFixed(2)}
                    </td>
                    <td className="px-4 sm:px-6 py-3.5 text-center whitespace-nowrap">
                      <span
                        className={`inline-block font-bold text-sm ${
                          p.stock === 0
                            ? 'text-rose-600'
                            : p.stock < p.minimum_stock
                            ? 'text-amber-600'
                            : 'text-slate-800'
                        }`}
                      >
                        {p.stock}
                      </span>
                    </td>
                    <td className="px-4 sm:px-6 py-3.5 text-center text-slate-500 font-medium whitespace-nowrap">
                      {p.minimum_stock}
                    </td>
                    <td className="px-4 sm:px-6 py-3.5 text-center whitespace-nowrap">
                      <InventoryStatusBadge status={status} />
                    </td>
                    <td className="px-4 sm:px-6 py-3.5 text-right whitespace-nowrap">
                      <div className="flex items-center justify-end gap-1">
                        <button
                          type="button"
                          onClick={() => onEdit(p)}
                          aria-label={`Editar ${p.name}`}
                          className="p-1.5 text-slate-500 hover:text-retail-700 hover:bg-slate-100 rounded-lg transition-colors"
                          title="Editar producto"
                        >
                          <Edit3 className="w-4 h-4" />
                        </button>
                        <button
                          type="button"
                          onClick={() => onDelete(p)}
                          aria-label={`Eliminar ${p.name}`}
                          className="p-1.5 text-slate-500 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
                          title="Eliminar producto"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Footer contador */}
      <div className="px-4 sm:px-6 py-3 border-t border-slate-100 bg-slate-50/50 text-xs text-slate-500 flex justify-between items-center">
        <span>Mostrando {filteredProducts.length} de {products.length} productos</span>
      </div>
    </div>
  );
};
