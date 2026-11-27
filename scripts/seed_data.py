#!/usr/bin/env python3
"""Script de inicialización de datos (seed) para RetailFlow AI.

Puebla el catálogo de productos con un lote representativo de retail (almacén,
bebidas, lácteos, limpieza y frescos), incluyendo productos con stock saludable,
bajo stock y agotados.

El script es idempotente: comprueba la existencia de cada SKU antes de insertar,
evitando duplicados o sobreescrituras en ejecuciones repetidas.

Uso:
    python scripts/seed_data.py
"""

import sys
from pathlib import Path

# Añadir la raíz del proyecto al sys.path para importar los módulos de app
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from sqlalchemy import select  # noqa: E402
from app.database import Base, SessionLocal, engine  # noqa: E402
from app.models.product import Product  # noqa: E402

SAMPLE_PRODUCTS = [
    # Almacén
    {
        "name": "Aceite de Girasol 1.5L",
        "sku": "ALM-ACE-001",
        "category": "Almacén",
        "price": 2850.0,
        "stock": 4,
        "minimum_stock": 10,  # Bajo stock (crítico)
    },
    {
        "name": "Arroz Largo Fino 1kg",
        "sku": "ALM-ARR-002",
        "category": "Almacén",
        "price": 1450.0,
        "stock": 35,
        "minimum_stock": 15,  # Saludable
    },
    {
        "name": "Fideos Spaghetti 500g",
        "sku": "ALM-FID-003",
        "category": "Almacén",
        "price": 980.0,
        "stock": 0,
        "minimum_stock": 20,  # Agotado (crítico urgente)
    },
    {
        "name": "Harina de Trigo 000 1kg",
        "sku": "ALM-HAR-004",
        "category": "Almacén",
        "price": 1120.0,
        "stock": 8,
        "minimum_stock": 15,  # Bajo stock (crítico)
    },
    # Bebidas
    {
        "name": "Agua Mineral sin Gas 2L",
        "sku": "BEB-AGU-001",
        "category": "Bebidas",
        "price": 1200.0,
        "stock": 50,
        "minimum_stock": 25,  # Saludable
    },
    {
        "name": "Gaseosa Cola 2.25L",
        "sku": "BEB-GAS-002",
        "category": "Bebidas",
        "price": 3100.0,
        "stock": 2,
        "minimum_stock": 15,  # Bajo stock (crítico)
    },
    {
        "name": "Jugo de Naranja 1L",
        "sku": "BEB-JUG-003",
        "category": "Bebidas",
        "price": 1850.0,
        "stock": 0,
        "minimum_stock": 12,  # Agotado (crítico urgente)
    },
    # Lácteos
    {
        "name": "Leche Entera UAT 1L",
        "sku": "LAC-LEC-001",
        "category": "Lácteos",
        "price": 1350.0,
        "stock": 5,
        "minimum_stock": 30,  # Bajo stock (crítico)
    },
    {
        "name": "Yogur Firme Vainilla 190g",
        "sku": "LAC-YOG-002",
        "category": "Lácteos",
        "price": 850.0,
        "stock": 22,
        "minimum_stock": 15,  # Saludable
    },
    {
        "name": "Queso Cremoso 1kg",
        "sku": "LAC-QUE-003",
        "category": "Lácteos",
        "price": 6400.0,
        "stock": 0,
        "minimum_stock": 8,  # Agotado (crítico urgente)
    },
    # Limpieza
    {
        "name": "Lavandina Común 1L",
        "sku": "LIM-LAV-001",
        "category": "Limpieza",
        "price": 1100.0,
        "stock": 40,
        "minimum_stock": 20,  # Saludable
    },
    {
        "name": "Detergente Vajilla 750ml",
        "sku": "LIM-DET-002",
        "category": "Limpieza",
        "price": 2150.0,
        "stock": 3,
        "minimum_stock": 10,  # Bajo stock (crítico)
    },
    # Frescos
    {
        "name": "Manzana Roja Seleccionada 1kg",
        "sku": "FRE-MAN-001",
        "category": "Frescos",
        "price": 2200.0,
        "stock": 18,
        "minimum_stock": 10,  # Saludable
    },
    {
        "name": "Pechuga de Pollo Fresca 1kg",
        "sku": "FRE-POL-002",
        "category": "Frescos",
        "price": 4900.0,
        "stock": 0,
        "minimum_stock": 10,  # Agotado (crítico urgente)
    },
]


def seed_database() -> None:
    """Inserta productos iniciales en la base de datos de manera idempotente."""
    # Asegura que las tablas existan (especialmente útil en bases vacías como PostgreSQL)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    inserted_count = 0
    skipped_count = 0

    try:
        print("[RetailFlow AI] Iniciando carga de datos semilla (seed)...")
        for item in SAMPLE_PRODUCTS:
            stmt = select(Product).where(Product.sku == item["sku"])
            existing = db.execute(stmt).scalar_one_or_none()

            if existing is None:
                new_product = Product(
                    name=item["name"],
                    sku=item["sku"],
                    category=item["category"],
                    price=item["price"],
                    stock=item["stock"],
                    minimum_stock=item["minimum_stock"],
                )
                db.add(new_product)
                inserted_count += 1
                print(f"  + Insertado: {item['sku']} - {item['name']} (Stock: {item['stock']})")
            else:
                skipped_count += 1
                print(f"  = Omitido (ya existe): {item['sku']} - {item['name']}")

        db.commit()
        print(f"\n[RetailFlow AI] Seed completado con éxito.")
        print(f"  - Nuevos insertados: {inserted_count}")
        print(f"  - Ya existentes (sin cambios): {skipped_count}")
        print(f"  - Total procesados: {len(SAMPLE_PRODUCTS)}")

    except Exception as exc:
        db.rollback()
        print(f"[Error] Falló la inserción de datos semilla: {exc}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
