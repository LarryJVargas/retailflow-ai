from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class InventoryStatus(str, Enum):
    LOW_STOCK = "LOW_STOCK"
    OUT_OF_STOCK = "OUT_OF_STOCK"
    HEALTHY = "HEALTHY"


class InventoryItemResponse(BaseModel):
    """Representación de un producto en el contexto de inventario con métricas calculadas."""
    id: int
    name: str
    sku: str
    category: str
    price: float
    stock: int
    minimum_stock: int
    status: InventoryStatus = Field(..., description="Estado de inventario (LOW_STOCK, OUT_OF_STOCK, HEALTHY)")
    suggested_restock: int = Field(
        ...,
        ge=0,
        description="Cantidad sugerida a reponer calculada como max(minimum_stock - stock, 0)",
    )

    model_config = ConfigDict(from_attributes=True)


class InventorySummaryResponse(BaseModel):
    """Resumen cuantitativo del inventario con categorías mutuamente excluyentes."""
    total_products: int = Field(..., ge=0, description="Total de productos registrados")
    low_stock_products: int = Field(..., ge=0, description="Productos con stock > 0 y menor al mínimo")
    out_of_stock_products: int = Field(..., ge=0, description="Productos con stock igual a cero")
    healthy_products: int = Field(..., ge=0, description="Productos con stock > 0 y mayor o igual al mínimo")
