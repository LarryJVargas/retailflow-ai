from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.ai import InventoryAnalysisResponse
from app.services import ai_service

router = APIRouter(prefix="/ai", tags=["AI Inventory Analysis"])


@router.post(
    "/analyze-inventory",
    response_model=InventoryAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analizar inventario crítico con Gemini AI",
    description=(
        "Evalúa los productos con stock bajo o agotados mediante Gemini API para "
        "proveer priorización inteligente y justificaciones contextuales. "
        "Las cantidades sugeridas son calculadas determinísticamente por el backend. "
        "Si la API no está configurada, falla o intenta modificar cantidades, "
        "se retorna automáticamente un análisis determinista con source='fallback'."
    ),
)
def analyze_inventory_endpoint(
    db: Session = Depends(get_db),
) -> InventoryAnalysisResponse:
    return ai_service.analyze_inventory(db)
