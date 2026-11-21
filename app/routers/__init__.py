from app.routers.ai import router as ai_router
from app.routers.health import router as health_router
from app.routers.inventory import router as inventory_router
from app.routers.products import router as products_router

__all__ = ["ai_router", "health_router", "inventory_router", "products_router"]
