from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class PriorityLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ProductRecommendation(BaseModel):
    """Recomendación individual de reposición validada por el backend."""
    sku: str = Field(..., description="Código SKU del producto analizado")
    explanation: str = Field(..., description="Explicación contextual y justificación de la reposición")
    priority: PriorityLevel = Field(..., description="Nivel de prioridad asignado (CRITICAL, HIGH, MEDIUM, LOW)")
    suggested_quantity: int = Field(
        ...,
        ge=0,
        description="Cantidad exacta calculada determinísticamente por el backend",
    )

    model_config = ConfigDict(from_attributes=True)


class GeminiRawRecommendation(BaseModel):
    """Esquema para validar la respuesta cruda emitida por el modelo Gemini."""
    sku: str
    explanation: str
    priority: PriorityLevel
    suggested_quantity: int


class GeminiRawResponse(BaseModel):
    """Esquema raíz para parsear la respuesta estructurada de Gemini."""
    summary: str = Field(default="Análisis de inventario generado por IA.")
    recommendations: list[GeminiRawRecommendation] = Field(default_factory=list)


class InventoryAnalysisResponse(BaseModel):
    """Respuesta final expuesta por la API para el análisis de inventario."""
    source: str = Field(
        ...,
        description="Origen del análisis: 'gemini' para análisis exitoso por IA o 'fallback' para reglas deterministas",
    )
    model_used: str | None = Field(
        default=None,
        description="Identificador del modelo Gemini utilizado, o None si se aplicó fallback",
    )
    summary: str = Field(..., description="Resumen ejecutivo del estado del inventario crítico")
    total_critical_products: int = Field(
        ...,
        ge=0,
        description="Total de productos críticos analizados que requieren reposición",
    )
    recommendations: list[ProductRecommendation] = Field(
        default_factory=list,
        description="Listado ordenado de recomendaciones por producto",
    )
