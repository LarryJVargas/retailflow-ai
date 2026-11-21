from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Nombre del producto",
        examples=["Remera Oversized Negra"],
    )
    sku: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Código único de identificación de inventario (SKU)",
        examples=["TSH-BLK-001"],
    )
    category: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Categoría o departamento",
        examples=["Indumentaria"],
    )
    price: float = Field(
        ...,
        ge=0.0,
        description="Precio del producto (no negativo)",
        examples=[24.99],
    )
    stock: int = Field(
        default=0,
        ge=0,
        description="Cantidad actual en inventario (no negativa)",
        examples=[50],
    )
    minimum_stock: int = Field(
        default=0,
        ge=0,
        description="Nivel mínimo de stock sugerido para alerta de reposición (no negativo)",
        examples=[10],
    )


class ProductCreate(ProductBase):
    """Esquema para la creación de un nuevo producto (POST /products)."""
    pass


class ProductUpdate(BaseModel):
    """Esquema para la actualización parcial de un producto (PATCH /products/{id})."""
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Nombre del producto",
        examples=["Remera Oversized Blanca"],
    )
    sku: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
        description="Código SKU",
        examples=["TSH-WHT-001"],
    )
    category: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
        description="Categoría o departamento",
        examples=["Indumentaria"],
    )
    price: float | None = Field(
        default=None,
        ge=0.0,
        description="Precio del producto",
        examples=[29.99],
    )
    stock: int | None = Field(
        default=None,
        ge=0,
        description="Stock actual",
        examples=[35],
    )
    minimum_stock: int | None = Field(
        default=None,
        ge=0,
        description="Stock mínimo",
        examples=[5],
    )


class ProductResponse(ProductBase):
    """Esquema de respuesta devuelto al cliente."""
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
