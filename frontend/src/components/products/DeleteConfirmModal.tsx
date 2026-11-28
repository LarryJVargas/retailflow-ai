import React from 'react';
import { AlertTriangle } from 'lucide-react';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';
import { Product } from '../../types/product';

interface DeleteConfirmModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => Promise<void>;
  product: Product | null;
  loading: boolean;
}

export const DeleteConfirmModal: React.FC<DeleteConfirmModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  product,
  loading,
}) => {
  if (!product) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Confirmar Eliminación" maxWidth="sm">
      <div className="space-y-4">
        <div className="flex items-start gap-3">
          <div className="p-2 rounded-full bg-rose-100 text-rose-600 shrink-0">
            <AlertTriangle className="w-5 h-5" />
          </div>
          <div>
            <p className="text-sm text-slate-700">
              ¿Estás seguro de que deseas eliminar permanentemente el producto{' '}
              <strong className="text-slate-900">{product.name}</strong> (SKU:{' '}
              <span className="font-mono text-xs font-bold text-slate-800">{product.sku}</span>)?
            </p>
            <p className="text-xs text-rose-600 font-medium mt-2">
              Esta acción no se puede deshacer.
            </p>
          </div>
        </div>

        <div className="pt-3 border-t border-slate-100 flex flex-col-reverse sm:flex-row sm:items-center sm:justify-end gap-2">
          <Button variant="outline" onClick={onClose} disabled={loading} size="sm" className="w-full sm:w-auto">
            Cancelar
          </Button>
          <Button variant="danger" onClick={onConfirm} loading={loading} size="sm" className="w-full sm:w-auto">
            Sí, Eliminar
          </Button>
        </div>
      </div>
    </Modal>
  );
};
