import csv
from datetime import datetime
import io
import os
from sqlalchemy.orm import Session

from app.services.inventory_service import get_low_stock_products, get_out_of_stock_products

CSV_HEADERS = [
    "SKU",
    "Nombre",
    "Categoría",
    "Stock Actual",
    "Stock Mínimo",
    "Estado",
    "Reposición Sugerida",
]


def generate_inventory_report_csv(db: Session) -> str:
    """Genera en memoria un archivo CSV con los productos con bajo stock y agotados.

    Retorna el contenido formateado en UTF-8 como cadena de texto.
    """
    out_of_stock_items = get_out_of_stock_products(db)
    low_stock_items = get_low_stock_products(db)

    # Combinamos: primero agotados (mayor urgencia), luego stock bajo
    critical_items = out_of_stock_items + low_stock_items

    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(CSV_HEADERS)

    for item in critical_items:
        writer.writerow(
            [
                item.sku,
                item.name,
                item.category,
                item.stock,
                item.minimum_stock,
                item.status.value,
                item.suggested_restock,
            ]
        )

    return output.getvalue()


def save_inventory_report_to_disk(db: Session, output_dir: str = "reports") -> str:
    """Genera y guarda el reporte CSV en el directorio indicado.

    Crea el directorio si no existe y utiliza una marca de tiempo en el nombre del archivo.
    Retorna la ruta del archivo generado.
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(output_dir, f"inventory_report_{timestamp}.csv")

    csv_content = generate_inventory_report_csv(db)
    with open(file_path, mode="w", encoding="utf-8", newline="") as file:
        file.write(csv_content)

    return file_path
