from fastapi import APIRouter, status
from pydantic import BaseModel

from app.config import get_settings

router = APIRouter(prefix="/health", tags=["Health"])
settings = get_settings()


class HealthResponse(BaseModel):
    status: str
    app: str
    environment: str


@router.get(
    "",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Verificar el estado del servicio",
    description="Devuelve el estado de ejecución de la aplicación y el entorno actual.",
)
def check_health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        app=settings.app_name,
        environment=settings.app_env,
    )
