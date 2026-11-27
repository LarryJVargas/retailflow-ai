from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "RetailFlow AI"
    app_env: str = "development"
    debug: bool = True
    database_url: str = "sqlite:///./retailflow.db"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.5-flash"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000"

    # Rate limiting — límites configurables por variable de entorno.
    # Formato: "<cantidad>/<unidad>" (ej. "10/minute", "100/hour").
    # Valor 0 o cadena vacía desactiva el límite para ese endpoint.
    rate_limit_write: str = "10/minute"    # POST y PATCH en /products
    rate_limit_delete: str = "5/minute"   # DELETE en /products
    rate_limit_ai: str = "3/minute"       # POST en /ai/analyze-inventory

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def resolved_database_url(self) -> str:
        """Normaliza el esquema de conexión de bases de datos.

        Muchos proveedores de hosting (Supabase, Render) entregan URLs que comienzan
        con 'postgres://' o 'postgresql://'. Se normalizan explícitamente a
        'postgresql+psycopg2://' para asegurar que SQLAlchemy 2.0 utilice el driver
        psycopg2-binary instalado en lugar de intentar cargar psycopg 3.
        """
        url = self.database_url.strip()
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+psycopg2://", 1)
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+psycopg2://", 1)
        return url

    @property
    def parsed_cors_origins(self) -> list[str]:
        """Convierte la cadena delimitada por comas en una lista de orígenes permitidos."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Retorna una instancia cacheada de la configuración de la app."""
    return Settings()
