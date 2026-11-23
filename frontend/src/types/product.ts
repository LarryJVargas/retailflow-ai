export interface Product {
  id: number;
  name: string;
  sku: string;
  category: string;
  price: number;
  stock: number;
  minimum_stock: number;
  created_at: string;
}

export interface ProductCreate {
  name: string;
  sku: string;
  category: string;
  price: number;
  stock: number;
  minimum_stock: number;
}

export interface ProductUpdate {
  name?: string;
  sku?: string;
  category?: string;
  price?: number;
  stock?: number;
  minimum_stock?: number;
}
