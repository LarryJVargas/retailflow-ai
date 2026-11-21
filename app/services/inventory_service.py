from collections.abc import Sequence
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.inventory import InventoryItemResponse, InventoryStatus, InventorySummaryResponse


def get_low_stock_products(db: Session) -> list[InventoryItemResponse]:
    """Obtiene los productos con stock mayor a cero pero inferior al stock mínimo configurado.

    Excluye productos agotados (stock == 0).
    Calcula la reposición sugerida como: max(minimum_stock - stock, 0).
    """
    stmt = (
        select(Product)
        .where(Product.stock > 0, Product.stock < Product.minimum_stock)
        .order_by(Product.stock.asc())
    )
    products: Sequence[Product] = db.scalars(stmt).all()

    return [
        InventoryItemResponse(
            id=p.id,
            name=p.name,
            sku=p.sku,
            category=p.category,
            price=p.price,
            stock=p.stock,
            minimum_stock=p.minimum_stock,
            status=InventoryStatus.LOW_STOCK,
            suggested_restock=max(p.minimum_stock - p.stock, 0),
        )
        for p in products
    ]


def get_out_of_stock_products(db: Session) -> list[InventoryItemResponse]:
    """Obtiene los productos cuyo stock actual es exactamente cero.

    Calcula la reposición sugerida según el stock mínimo: max(minimum_stock - stock, 0).
    Si minimum_stock es 0, la reposición sugerida será 0.
    """
    stmt = select(Product).where(Product.stock == 0).order_by(Product.id.asc())
    products: Sequence[Product] = db.scalars(stmt).all()

    return [
        InventoryItemResponse(
            id=p.id,
            name=p.name,
            sku=p.sku,
            category=p.category,
            price=p.price,
            stock=p.stock,
            minimum_stock=p.minimum_stock,
            status=InventoryStatus.OUT_OF_STOCK,
            suggested_restock=max(p.minimum_stock - p.stock, 0),
        )
        for p in products
    ]


def get_inventory_summary(db: Session) -> InventorySummaryResponse:
    """Calcula el resumen métrico cuantitativo del inventario.

    Garantiza categorías mutuamente excluyentes y exhaustivas:
    total_products = out_of_stock_products + low_stock_products + healthy_products.

    Comportamiento con minimum_stock == 0:
    - Si stock == 0: clasifica como 'out_of_stock_products' (el producto no tiene existencias físicas).
    - Si stock > 0: clasifica como 'healthy_products' (cumple stock >= minimum_stock y stock > 0).
    - Un producto con minimum_stock == 0 nunca entrará en 'low_stock_products' porque es imposible
      cumplir simultáneamente 0 < stock < 0.
    """
    total = db.scalar(select(func.count(Product.id))) or 0
    out_of_stock = db.scalar(select(func.count(Product.id)).where(Product.stock == 0)) or 0
    low_stock = (
        db.scalar(
            select(func.count(Product.id)).where(
                Product.stock > 0,
                Product.stock < Product.minimum_stock,
            )
        )
        or 0
    )
    healthy = (
        db.scalar(
            select(func.count(Product.id)).where(
                Product.stock > 0,
                Product.stock >= Product.minimum_stock,
            )
        )
        or 0
    )

    return InventorySummaryResponse(
        total_products=total,
        low_stock_products=low_stock,
        out_of_stock_products=out_of_stock,
        healthy_products=healthy,
    )
