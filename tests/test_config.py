from app.config import Settings


def test_resolved_database_url_converts_postgres_and_postgresql_schemes() -> None:
    """Verifica que 'postgres://' y 'postgresql://' se normalicen a 'postgresql+psycopg2://'."""
    postgres_settings = Settings(
        database_url="postgres://user:password@db.supabase.co:5432/postgres?sslmode=require",
        _env_file=None,
    )
    assert (
        postgres_settings.resolved_database_url
        == "postgresql+psycopg2://user:password@db.supabase.co:5432/postgres?sslmode=require"
    )

    postgresql_settings = Settings(
        database_url="postgresql://user:password@aws-0-sa-east-1.pooler.supabase.com:5432/postgres?sslmode=require",
        _env_file=None,
    )
    assert (
        postgresql_settings.resolved_database_url
        == "postgresql+psycopg2://user:password@aws-0-sa-east-1.pooler.supabase.com:5432/postgres?sslmode=require"
    )


def test_resolved_database_url_preserves_psycopg2_and_sqlite() -> None:
    """Verifica que 'postgresql+psycopg2://' y 'sqlite:///' permanezcan intactos."""
    sqlite_settings = Settings(database_url="sqlite:///./test.db", _env_file=None)
    assert sqlite_settings.resolved_database_url == "sqlite:///./test.db"

    pg_settings = Settings(
        database_url="postgresql+psycopg2://user:pass@localhost:5432/db?sslmode=require",
        _env_file=None,
    )
    assert pg_settings.resolved_database_url == "postgresql+psycopg2://user:pass@localhost:5432/db?sslmode=require"


def test_parsed_cors_origins_splits_and_trims() -> None:
    """Verifica la división por comas y limpieza de espacios de orígenes CORS."""
    settings = Settings(
        cors_origins="https://retailflow-ai.vercel.app, http://localhost:5173 , http://127.0.0.1:5173",
        _env_file=None,
    )
    assert settings.parsed_cors_origins == [
        "https://retailflow-ai.vercel.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


def test_parsed_cors_origins_empty_string() -> None:
    """Verifica el comportamiento con una cadena vacía o sólo comas."""
    settings = Settings(cors_origins="  ,  ,  ", _env_file=None)
    assert settings.parsed_cors_origins == []
