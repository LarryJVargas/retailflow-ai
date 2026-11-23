export type PriorityLevel = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';

export interface ProductRecommendation {
  sku: string;
  explanation: string;
  priority: PriorityLevel;
  suggested_quantity: number;
}

export interface InventoryAnalysisResponse {
  source: 'gemini' | 'fallback';
  model_used: string | null;
  summary: string;
  total_critical_products: number;
  recommendations: ProductRecommendation[];
}
