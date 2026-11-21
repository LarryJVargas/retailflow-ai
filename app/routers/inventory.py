from datetime import datetime
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.inventory import InventoryItemResponse, InventorySummaryResponse
from app.services import inventory_service, report_service

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get(
    "/low-stock",
    response_model=list[InventoryItemResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar productos con stock bajo",
    description=(
        "Retorna los productos que tienen existencias mayores a cero pero por debajo "
        "de su stock mínimo configurado. Excluye productos totalmente agotados e incluye "
        "la cantidad sugerida de reposición."
    ),
)
def list_low_stock_products(
    db: Session = Depends(get_db),
) -> list[InventoryItemResponse]:
    return inventory_service.get_low_stock_products(db)


@router.get(
    "/out-of-stock",
    response_model=list[InventoryItemResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar productos agotados",
    description=(
        "Retorna todos los productos con stock exactamente igual a cero, "
        "calculando la cantidad sugerida para reabastecimiento."
    ),
)
def list_out_of_stock_products(
    db: Session = Depends(get_db),
) -> list[InventoryItemResponse]:
    return inventory_service.get_out_of_stock_products(db)


@router.get(
    "/summary",
    response_model=InventorySummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener resumen general del inventario",
    description=(
        "Devuelve las métricas cuantitativas del inventario divididas en categorías "
        "mutuamente excluyentes: total de productos, productos con stock bajo, "
        "productos agotados y productos saludables."
    ),
)
def get_inventory_summary(
    db: Session = Depends(get_db),
) -> InventorySummaryResponse:
    return inventory_service.get_inventory_summary(db)


@router.get(
    "/report",
    status_code=status.HTTP_200_OK,
    summary="Exportar reporte de inventario en CSV",
    description=(
        "Genera dinámicamente y descarga un archivo CSV con el detalle de productos "
        "en estado crítico (agotados y con bajo stock), incluyendo la sugerencia de reposición."
    ),
)
def download_inventory_report(
    db: Session = Depends(get_db),
) -> Response:
    csv_content = report_service.generate_inventory_report_csv(db)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"inventory_report_{timestamp}.csv"

    return Response(
        content=csv_content,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )
