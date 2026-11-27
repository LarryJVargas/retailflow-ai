from collections.abc import Sequence
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.limiter import limiter
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.config import get_settings

router = APIRouter(prefix="/products", tags=["Products"])
settings = get_settings()


@router.get(
    "",
    response_model=list[ProductResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar productos",
    description="Obtiene el listado de productos registrados en el inventario con soporte de paginación básica.",
)
def list_products(
    skip: int = Query(0, ge=0, description="Número de registros a omitir para paginación"),
    limit: int = Query(100, ge=1, le=500, description="Cantidad máxima de productos a devolver"),
    db: Session = Depends(get_db),
) -> Sequence[Product]:
    query = select(Product).offset(skip).limit(limit).order_by(Product.id.asc())
    return db.scalars(query).all()


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener un producto por ID",
    description="Retorna la información detallada de un producto específico mediante su ID numérico.",
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
) -> Product:
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con id {product_id} no encontrado.",
        )
    return product


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo producto",
    description="Registra un nuevo producto en el catálogo. El código SKU debe ser único.",
)
@limiter.shared_limit(lambda: get_settings().rate_limit_write, scope="products:write")
def create_product(
    request: Request,
    payload: ProductCreate,
    db: Session = Depends(get_db),
) -> Product:
    # Validar unicidad del SKU
    existing = db.scalars(select(Product).where(Product.sku == payload.sku)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un producto registrado con el SKU '{payload.sku}'.",
        )

    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.patch(
    "/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar parcialmente un producto",
    description="Permite modificar uno o varios atributos de un producto existente.",
)
@limiter.shared_limit(lambda: get_settings().rate_limit_write, scope="products:write")
def update_product(
    request: Request,
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
) -> Product:
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con id {product_id} no encontrado.",
        )

    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        return product

    # Si se intenta cambiar el SKU, validar que no choque con otro producto
    if "sku" in update_data and update_data["sku"] != product.sku:
        existing_sku = db.scalars(
            select(Product).where(
                Product.sku == update_data["sku"],
                Product.id != product_id,
            )
        ).first()
        if existing_sku:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe otro producto con el SKU '{update_data['sku']}'.",
            )

    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un producto",
    description="Elimina permanentemente un producto del catálogo por su ID.",
)
@limiter.shared_limit(lambda: get_settings().rate_limit_delete, scope="products:delete")
def delete_product(
    request: Request,
    product_id: int,
    db: Session = Depends(get_db),
) -> None:
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con id {product_id} no encontrado.",
        )

    db.delete(product)
    db.commit()
    return None
