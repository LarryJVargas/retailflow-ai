#!/usr/bin/env python3
"""Script CLI para generar el reporte de inventario crítico en formato CSV.

Uso:
    python scripts/generate_report.py
"""

import sys
from pathlib import Path

# Añadir la raíz del proyecto al sys.path para importar los módulos de app
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.database import SessionLocal  # noqa: E402
from app.services.report_service import save_inventory_report_to_disk  # noqa: E402


def main() -> None:
    db = SessionLocal()
    try:
        report_path = save_inventory_report_to_disk(db=db, output_dir=str(BASE_DIR / "reports"))
        print(f"[RetailFlow AI] Reporte de inventario generado exitosamente:")
        print(f" -> {report_path}")
    except Exception as exc:
        print(f"[Error] Falló la generación del reporte: {exc}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
