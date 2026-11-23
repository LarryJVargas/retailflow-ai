import { useState, useEffect, useCallback } from 'react';
import { Sidebar, NavigationTab } from './components/layout/Sidebar';
import { Header } from './components/layout/Header';
import { KpiCards } from './components/dashboard/KpiCards';
import { ProductTable } from './components/products/ProductTable';
import { ProductModal } from './components/products/ProductModal';
import { DeleteConfirmModal } from './components/products/DeleteConfirmModal';
import { CriticalInventoryView } from './components/inventory/CriticalInventoryView';
import { AiAnalysisPanel } from './components/ai/AiAnalysisPanel';
import { Notification, NotificationState } from './components/common/Notification';
import { api, ApiError } from './services/api';
import { Product, ProductCreate, ProductUpdate } from './types/product';
import { InventorySummary, InventoryItem } from './types/inventory';
import { InventoryAnalysisResponse } from './types/ai';

export default function App() {
  const [currentTab, setCurrentTab] = useState<NavigationTab>('dashboard');

  // Estados de datos
  const [products, setProducts] = useState<Product[]>([]);
  const [summary, setSummary] = useState<InventorySummary | null>(null);
  const [lowStockItems, setLowStockItems] = useState<InventoryItem[]>([]);
  const [outOfStockItems, setOutOfStockItems] = useState<InventoryItem[]>([]);
  const [aiAnalysis, setAiAnalysis] = useState<InventoryAnalysisResponse | null>(null);

  // Estados de UI y carga
  const [loading, setLoading] = useState<boolean>(true);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [isDownloadingReport, setIsDownloadingReport] = useState<boolean>(false);
  const [isAiLoading, setIsAiLoading] = useState<boolean>(false);
  const [aiError, setAiError] = useState<string | null>(null);

  // Modales
  const [isProductModalOpen, setIsProductModalOpen] = useState<boolean>(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [isSubmittingProduct, setIsSubmittingProduct] = useState<boolean>(false);
  const [productModalError, setProductModalError] = useState<string | null>(null);

  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState<boolean>(false);
  const [deletingProduct, setDeletingProduct] = useState<Product | null>(null);
  const [isDeleting, setIsDeleting] = useState<boolean>(false);

  // Notificaciones
  const [notification, setNotification] = useState<NotificationState | null>(null);

  const showNotification = (type: 'success' | 'error' | 'info', message: string) => {
    setNotification({ type, message });
    setTimeout(() => {
      setNotification((prev) => (prev?.message === message ? null : prev));
    }, 5000);
  };

  // Carga inicial y refresco de datos
  const loadData = useCallback(async (quiet = false) => {
    if (!quiet) setLoading(true);
    else setIsRefreshing(true);

    try {
      const [prodsData, summaryData, lowData, outData] = await Promise.all([
        api.getProducts(0, 500),
        api.getInventorySummary(),
        api.getLowStockProducts(),
        api.getOutOfStockProducts(),
      ]);

      setProducts(prodsData);
      setSummary(summaryData);
      setLowStockItems(lowData);
      setOutOfStockItems(outData);
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : 'Error al conectar con el backend de RetailFlow AI.';
      showNotification('error', msg);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Manejo de productos (Crear / Editar)
  const handleOpenCreateModal = () => {
    setEditingProduct(null);
    setProductModalError(null);
    setIsProductModalOpen(true);
  };

  const handleOpenEditModal = (product: Product) => {
    setEditingProduct(product);
    setProductModalError(null);
    setIsProductModalOpen(true);
  };

  const handleSaveProduct = async (data: ProductCreate | ProductUpdate) => {
    setIsSubmittingProduct(true);
    setProductModalError(null);
    try {
      if (editingProduct) {
        await api.updateProduct(editingProduct.id, data as ProductUpdate);
        showNotification('success', `Producto '${editingProduct.sku}' actualizado correctamente.`);
      } else {
        const created = await api.createProduct(data as ProductCreate);
        showNotification('success', `Producto '${created.sku}' creado con éxito.`);
      }
      setIsProductModalOpen(false);
      await loadData(true);
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.status === 409) {
          setProductModalError('Conflicto: Ya existe un producto con el código SKU ingresado.');
        } else {
          setProductModalError(err.message);
        }
      } else {
        setProductModalError('Error inesperado al guardar el producto.');
      }
    } finally {
      setIsSubmittingProduct(false);
    }
  };

  // Manejo de eliminación
  const handleOpenDeleteModal = (product: Product) => {
    setDeletingProduct(product);
    setIsDeleteModalOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!deletingProduct) return;
    setIsDeleting(true);
    try {
      await api.deleteProduct(deletingProduct.id);
      showNotification('success', `Producto '${deletingProduct.sku}' eliminado.`);
      setIsDeleteModalOpen(false);
      await loadData(true);
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : 'Error al eliminar producto.';
      showNotification('error', msg);
    } finally {
      setIsDeleting(false);
    }
  };

  // Descarga de reporte CSV
  const handleDownloadReport = async () => {
    setIsDownloadingReport(true);
    try {
      const { blob, filename } = await api.downloadInventoryReport();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      showNotification('success', `Reporte '${filename}' descargado correctamente.`);
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : 'Fallo en la descarga del CSV.';
      showNotification('error', msg);
    } finally {
      setIsDownloadingReport(false);
    }
  };

  // Ejecución de análisis de IA
  const handleRunAiAnalysis = async () => {
    setIsAiLoading(true);
    setAiError(null);
    try {
      const result = await api.analyzeInventory();
      setAiAnalysis(result);
      if (result.source === 'gemini') {
        showNotification('success', `Análisis completado exitosamente mediante Gemini (${result.model_used || 'gemini-3.5-flash'}).`);
      } else {
        showNotification('info', 'Análisis completado mediante motor determinista de contingencia (Fallback).');
      }
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : 'No se pudo obtener el análisis.';
      setAiError(msg);
      showNotification('error', msg);
    } finally {
      setIsAiLoading(false);
    }
  };

  const criticalCount = lowStockItems.length + outOfStockItems.length;

  const getPageTitle = () => {
    switch (currentTab) {
      case 'dashboard':
        return { title: 'Panel General de Inventario', subtitle: 'Métricas de disponibilidad en tiempo real y estado de catálogo' };
      case 'products':
        return { title: 'Catálogo de Productos', subtitle: 'Administración, altas, modificaciones y control de existencias' };
      case 'critical':
        return { title: 'Inventario Crítico', subtitle: 'Artículos con necesidad inmediata de reposición en góndola' };
      case 'ai':
        return { title: 'Análisis Asistido con Gemini AI', subtitle: 'Diagnóstico contextual y priorización de reaprovisionamiento' };
    }
  };

  const { title, subtitle } = getPageTitle();

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden">
      {/* Sidebar fijo */}
      <Sidebar
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        criticalCount={criticalCount}
      />

      {/* Área principal */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Header superior */}
        <Header
          title={title}
          subtitle={subtitle}
          onDownloadReport={handleDownloadReport}
          onOpenCreateModal={handleOpenCreateModal}
          onRefresh={() => loadData(true)}
          isDownloadingReport={isDownloadingReport}
          isRefreshing={isRefreshing}
        />

        {/* Notificación flotante / Toast */}
        <div className="fixed bottom-5 right-5 z-50 max-w-md w-full px-4 pointer-events-none">
          <div className="pointer-events-auto">
            <Notification
              notification={notification}
              onClose={() => setNotification(null)}
            />
          </div>
        </div>

        {/* Contenido scrolleable */}
        <main className="flex-1 overflow-y-auto p-6 space-y-6">
          {currentTab === 'dashboard' && (
            <div className="space-y-6">
              <KpiCards summary={summary} loading={loading} />

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h2 className="text-sm font-bold uppercase tracking-wider text-slate-700">
                    Artículos en Catálogo
                  </h2>
                  <button
                    onClick={() => setCurrentTab('products')}
                    className="text-xs font-semibold text-retail-700 hover:text-retail-800"
                  >
                    Ver catálogo completo &rarr;
                  </button>
                </div>
                <ProductTable
                  products={products}
                  loading={loading}
                  onEdit={handleOpenEditModal}
                  onDelete={handleOpenDeleteModal}
                />
              </div>
            </div>
          )}

          {currentTab === 'products' && (
            <div className="space-y-4">
              <ProductTable
                products={products}
                loading={loading}
                onEdit={handleOpenEditModal}
                onDelete={handleOpenDeleteModal}
              />
            </div>
          )}

          {currentTab === 'critical' && (
            <CriticalInventoryView
              lowStockItems={lowStockItems}
              outOfStockItems={outOfStockItems}
              loading={loading}
              onNavigateToAi={() => setCurrentTab('ai')}
            />
          )}

          {currentTab === 'ai' && (
            <AiAnalysisPanel
              analysis={aiAnalysis}
              loading={isAiLoading}
              onRunAnalysis={handleRunAiAnalysis}
              error={aiError}
            />
          )}
        </main>
      </div>

      {/* Modal de Crear / Editar Producto */}
      <ProductModal
        isOpen={isProductModalOpen}
        onClose={() => setIsProductModalOpen(false)}
        onSubmit={handleSaveProduct}
        product={editingProduct}
        loading={isSubmittingProduct}
        error={productModalError}
      />

      {/* Modal de Confirmar Eliminación */}
      <DeleteConfirmModal
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        onConfirm={handleConfirmDelete}
        product={deletingProduct}
        loading={isDeleting}
      />
    </div>
  );
}
