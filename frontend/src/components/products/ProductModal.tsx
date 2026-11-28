import React, { useState, useEffect } from 'react';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';
import { Product, ProductCreate, ProductUpdate } from '../../types/product';

interface ProductModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: ProductCreate | ProductUpdate) => Promise<void>;
  product?: Product | null;
  loading: boolean;
  error?: string | null;
}

export const ProductModal: React.FC<ProductModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  product,
  loading,
  error,
}) => {
  const isEditing = Boolean(product);

  const [formData, setFormData] = useState({
    name: '',
    sku: '',
    category: '',
    price: '',
    stock: '',
    minimum_stock: '',
  });

  const [localErrors, setLocalErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (product) {
      setFormData({
        name: product.name,
        sku: product.sku,
        category: product.category,
        price: product.price.toString(),
        stock: product.stock.toString(),
        minimum_stock: product.minimum_stock.toString(),
      });
    } else {
      setFormData({
        name: '',
        sku: '',
        category: '',
        price: '',
        stock: '0',
        minimum_stock: '5',
      });
    }
    setLocalErrors({});
  }, [product, isOpen]);

  const validate = (): boolean => {
    const errs: Record<string, string> = {};

    if (!formData.name.trim()) errs.name = 'El nombre es obligatorio.';
    if (!formData.sku.trim()) errs.sku = 'El código SKU es obligatorio.';
    if (!formData.category.trim()) errs.category = 'La categoría es obligatoria.';

    const priceNum = parseFloat(formData.price);
    if (isNaN(priceNum) || priceNum < 0) {
      errs.price = 'El precio debe ser un número mayor o igual a 0.';
    }

    const stockNum = parseInt(formData.stock, 10);
    if (isNaN(stockNum) || stockNum < 0) {
      errs.stock = 'El stock debe ser un entero no negativo.';
    }

    const minStockNum = parseInt(formData.minimum_stock, 10);
    if (isNaN(minStockNum) || minStockNum < 0) {
      errs.minimum_stock = 'El stock mínimo debe ser un entero no negativo.';
    }

    setLocalErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    const payload = {
      name: formData.name.trim(),
      sku: formData.sku.trim().toUpperCase(),
      category: formData.category.trim(),
      price: parseFloat(formData.price),
      stock: parseInt(formData.stock, 10),
      minimum_stock: parseInt(formData.minimum_stock, 10),
    };

    await onSubmit(payload);
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEditing ? `Editar Producto: ${product?.sku}` : 'Registrar Nuevo Producto'}
      maxWidth="md"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="p-3 text-xs rounded-lg bg-rose-50 border border-rose-200 text-rose-700 font-medium">
            {error}
          </div>
        )}

        <div>
          <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
            Nombre del Producto *
          </label>
          <input
            type="text"
            required
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="ej. Arroz Largo Fino 1kg"
            className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-retail-600 focus:border-transparent"
          />
          {localErrors.name && <p className="text-xs text-rose-600 mt-1">{localErrors.name}</p>}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
              Código SKU *
            </label>
            <input
              type="text"
              required
              value={formData.sku}
              onChange={(e) => setFormData({ ...formData, sku: e.target.value })}
              placeholder="ej. ARR-LAR-001"
              className="w-full px-3 py-2 text-sm font-mono border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-retail-600 focus:border-transparent uppercase"
            />
            {localErrors.sku && <p className="text-xs text-rose-600 mt-1">{localErrors.sku}</p>}
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
              Categoría *
            </label>
            <input
              type="text"
              required
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              placeholder="ej. Almacén"
              className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-retail-600 focus:border-transparent"
            />
            {localErrors.category && <p className="text-xs text-rose-600 mt-1">{localErrors.category}</p>}
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
            Precio Unitario ($) *
          </label>
          <input
            type="number"
            step="0.01"
            min="0"
            required
            value={formData.price}
            onChange={(e) => setFormData({ ...formData, price: e.target.value })}
            placeholder="0.00"
            className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-retail-600 focus:border-transparent"
          />
          {localErrors.price && <p className="text-xs text-rose-600 mt-1">{localErrors.price}</p>}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
              Stock Actual *
            </label>
            <input
              type="number"
              min="0"
              required
              value={formData.stock}
              onChange={(e) => setFormData({ ...formData, stock: e.target.value })}
              className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-retail-600 focus:border-transparent"
            />
            {localErrors.stock && <p className="text-xs text-rose-600 mt-1">{localErrors.stock}</p>}
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
              Stock Mínimo (Alerta) *
            </label>
            <input
              type="number"
              min="0"
              required
              value={formData.minimum_stock}
              onChange={(e) => setFormData({ ...formData, minimum_stock: e.target.value })}
              className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-retail-600 focus:border-transparent"
            />
            {localErrors.minimum_stock && (
              <p className="text-xs text-rose-600 mt-1">{localErrors.minimum_stock}</p>
            )}
          </div>
        </div>

        <div className="pt-4 border-t border-slate-100 flex flex-col-reverse sm:flex-row sm:items-center sm:justify-end gap-2.5">
          <Button type="button" variant="outline" onClick={onClose} disabled={loading} className="w-full sm:w-auto">
            Cancelar
          </Button>
          <Button type="submit" variant="primary" loading={loading} className="w-full sm:w-auto">
            {isEditing ? 'Guardar Cambios' : 'Registrar Producto'}
          </Button>
        </div>
      </form>
    </Modal>
  );
};
