from collections.abc import Generator
from typing import Any
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

settings = get_settings()
db_url = settings.resolved_database_url
is_sqlite = db_url.startswith("sqlite")

# Configuración defensiva según el motor de base de datos
engine_kwargs: dict[str, Any] = {"echo": settings.debug}

if is_sqlite:
    # check_same_thread solo aplica a SQLite para permitir múltiples hilos en FastAPI
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # Para PostgreSQL (Supabase / Render):
    # pool_pre_ping previene desconexiones por inactividad y pool_recycle evita sockets caídos
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_recycle"] = 300

engine = create_engine(
    db_url,
    **engine_kwargs,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Clase base declarativa para los modelos de SQLAlchemy 2.0."""
    pass


def get_db() -> Generator[Session, None, None]:
    """Generador de sesiones de base de datos para inyección de dependencias."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
