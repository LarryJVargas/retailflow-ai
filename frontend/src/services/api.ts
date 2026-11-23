import { Product, ProductCreate, ProductUpdate } from '../types/product';
import { InventoryItem, InventorySummary } from '../types/inventory';
import { InventoryAnalysisResponse } from '../types/ai';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '');

export class ApiError extends Error {
  status: number;
  details?: unknown;

  constructor(status: number, message: string, details?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.details = details;
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorMessage = `Error HTTP ${response.status}: ${response.statusText}`;
    let details: unknown = null;

    try {
      const errorJson = await response.json();
      details = errorJson;

      if (errorJson.detail) {
        if (typeof errorJson.detail === 'string') {
          errorMessage = errorJson.detail;
        } else if (Array.isArray(errorJson.detail)) {
          // Errores de validación Pydantic 422
          errorMessage = errorJson.detail.map((err: { loc?: string[]; msg?: string }) => {
            const field = err.loc ? err.loc.join('.') : '';
            return `${field}: ${err.msg}`;
          }).join(' | ');
        }
      }
    } catch {
      // No era JSON, usar texto por defecto
    }

    throw new ApiError(response.status, errorMessage, details);
  }

  if (response.status === 204) {
    return null as T;
  }

  return response.json();
}

export const api = {
  // Productos (CRUD)
  async getProducts(skip = 0, limit = 100): Promise<Product[]> {
    const res = await fetch(`${API_BASE_URL}/products?skip=${skip}&limit=${limit}`);
    return handleResponse<Product[]>(res);
  },

  async getProductById(id: number): Promise<Product> {
    const res = await fetch(`${API_BASE_URL}/products/${id}`);
    return handleResponse<Product>(res);
  },

  async createProduct(payload: ProductCreate): Promise<Product> {
    const res = await fetch(`${API_BASE_URL}/products`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<Product>(res);
  },

  async updateProduct(id: number, payload: ProductUpdate): Promise<Product> {
    const res = await fetch(`${API_BASE_URL}/products/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<Product>(res);
  },

  async deleteProduct(id: number): Promise<void> {
    const res = await fetch(`${API_BASE_URL}/products/${id}`, {
      method: 'DELETE',
    });
    return handleResponse<void>(res);
  },

  // Inventario
  async getInventorySummary(): Promise<InventorySummary> {
    const res = await fetch(`${API_BASE_URL}/inventory/summary`);
    return handleResponse<InventorySummary>(res);
  },

  async getLowStockProducts(): Promise<InventoryItem[]> {
    const res = await fetch(`${API_BASE_URL}/inventory/low-stock`);
    return handleResponse<InventoryItem[]>(res);
  },

  async getOutOfStockProducts(): Promise<InventoryItem[]> {
    const res = await fetch(`${API_BASE_URL}/inventory/out-of-stock`);
    return handleResponse<InventoryItem[]>(res);
  },

  async downloadInventoryReport(): Promise<{ blob: Blob; filename: string }> {
    const res = await fetch(`${API_BASE_URL}/inventory/report`);
    if (!res.ok) {
      throw new ApiError(res.status, 'Error al descargar el reporte de inventario');
    }

    const disposition = res.headers.get('Content-Disposition') || '';
    let filename = 'inventory_report.csv';
    const match = disposition.match(/filename="?([^";]+)"?/);
    if (match && match[1]) {
      filename = match[1];
    }

    const blob = await res.blob();
    return { blob, filename };
  },

  // IA - Análisis de Inventario
  async analyzeInventory(): Promise<InventoryAnalysisResponse> {
    const res = await fetch(`${API_BASE_URL}/ai/analyze-inventory`, {
      method: 'POST',
    });
    return handleResponse<InventoryAnalysisResponse>(res);
  },
};
