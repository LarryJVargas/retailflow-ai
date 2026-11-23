export type InventoryStatus = 'LOW_STOCK' | 'OUT_OF_STOCK' | 'HEALTHY';

export interface InventoryItem {
  id: number;
  name: string;
  sku: string;
  category: string;
  price: number;
  stock: number;
  minimum_stock: number;
  status: InventoryStatus;
  suggested_restock: number;
}

export interface InventorySummary {
  total_products: number;
  low_stock_products: number;
  out_of_stock_products: number;
  healthy_products: number;
}
