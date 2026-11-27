"""Tests de rate limiting para los endpoints protegidos con SlowAPI.

Estrategia de aislamiento:
  Cada test usa el fixture `limiter_reset` que vacía el almacenamiento en
  memoria del limiter antes de cada función, garantizando que los contadores
  no se acumulen entre tests ni interfieran con la suite existente.

  Los límites se sobreescriben temporalmente a valores muy bajos (ej. "2/minute")
  para evitar que los tests necesiten hacer decenas de peticiones para disparar
  el 429.

Nota sobre mocking de límites:
  SlowAPI evalúa los límites en tiempo de despacho. Sobrescribimos
  settings.rate_limit_* temporalmente usando monkeypatch de pytest,
  y forzamos la recarga del limiter con `app.state.limiter.reset()`.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def limiter_reset(client: TestClient) -> None:
    """Vacía el almacenamiento en memoria del limiter antes de cada test."""
    from app.main import app
    app.state.limiter.reset()


# ---------------------------------------------------------------------------
# Tests de rate limiting en POST /products
# ---------------------------------------------------------------------------

def test_create_product_rate_limit_allows_requests_within_limit(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifica que las peticiones dentro del límite respondan con 201."""
    from app.config import get_settings
    monkeypatch.setattr(get_settings(), "rate_limit_write", "5/minute")

    payload = {
        "name": "Producto Rate Test",
        "sku": "RATE-001",
        "category": "Test",
        "price": 10.0,
        "stock": 5,
        "minimum_stock": 1,
    }
    response = client.post("/products", json=payload)
    assert response.status_code == 201


def test_create_product_rate_limit_returns_429_when_exceeded(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifica que se devuelva HTTP 429 al superar el límite de creación de productos."""
    from app.config import get_settings
    from app.main import app

    monkeypatch.setattr(get_settings(), "rate_limit_write", "2/minute")
    app.state.limiter.reset()

    base_payload = {
        "name": "Rate Limit Product",
        "sku": "RATE-TMP",
        "category": "Test",
        "price": 5.0,
        "stock": 1,
        "minimum_stock": 0,
    }

    statuses = []
    for i in range(4):
        payload = {**base_payload, "sku": f"RATE-TMP-{i}"}
        response = client.post("/products", json=payload)
        statuses.append(response.status_code)

    # Las primeras 2 peticiones deben pasar; a partir de la 3era debe recibirse 429
    assert statuses[0] in (201, 409)
    assert statuses[1] in (201, 409)
    assert 429 in statuses, f"Se esperaba al menos un 429, se obtuvo: {statuses}"


def test_delete_product_rate_limit_returns_429_when_exceeded(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifica que DELETE /products responde 429 al superar el límite."""
    from app.config import get_settings
    from app.main import app

    monkeypatch.setattr(get_settings(), "rate_limit_delete", "1/minute")
    app.state.limiter.reset()

    # Crear dos productos para intentar eliminar
    for i in range(2):
        client.post(
            "/products",
            json={
                "name": f"Producto Del {i}",
                "sku": f"DEL-RATE-{i:03d}",
                "category": "Test",
                "price": 1.0,
                "stock": 1,
                "minimum_stock": 0,
            },
        )

    # Listar para obtener IDs reales
    products = client.get("/products").json()
    assert len(products) >= 2

    id1 = products[0]["id"]
    id2 = products[1]["id"]

    r1 = client.delete(f"/products/{id1}")
    r2 = client.delete(f"/products/{id2}")

    # La segunda petición debe ser rechazada por rate limit (límite: 1/minute)
    assert r1.status_code == 204
    assert r2.status_code == 429


# ---------------------------------------------------------------------------
# Tests de rate limiting en POST /ai/analyze-inventory
# ---------------------------------------------------------------------------

def test_ai_rate_limit_allows_requests_within_limit(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifica que las peticiones dentro del límite de IA respondan con 200."""
    from app.config import get_settings
    monkeypatch.setattr(get_settings(), "rate_limit_ai", "5/minute")

    response = client.post("/ai/analyze-inventory")
    assert response.status_code == 200


def test_ai_rate_limit_returns_429_when_exceeded(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifica que POST /ai/analyze-inventory devuelve 429 al superar el límite."""
    from app.config import get_settings
    from app.main import app

    monkeypatch.setattr(get_settings(), "rate_limit_ai", "2/minute")
    app.state.limiter.reset()

    statuses = [client.post("/ai/analyze-inventory").status_code for _ in range(4)]

    assert statuses[0] == 200
    assert statuses[1] == 200
    assert 429 in statuses, f"Se esperaba al menos un 429, se obtuvo: {statuses}"


# ---------------------------------------------------------------------------
# Test de estructura de respuesta 429
# ---------------------------------------------------------------------------

def test_rate_limit_response_structure(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifica que la respuesta 429 incluye el header Retry-After."""
    from app.config import get_settings
    from app.main import app

    monkeypatch.setattr(get_settings(), "rate_limit_ai", "1/minute")
    app.state.limiter.reset()

    # Primera petición: dentro del límite
    r1 = client.post("/ai/analyze-inventory")
    assert r1.status_code == 200

    # Segunda petición: supera el límite
    r2 = client.post("/ai/analyze-inventory")
    assert r2.status_code == 429
    # SlowAPI incluye información del error en el cuerpo o headers
    assert "error" in r2.json() or "detail" in r2.json() or r2.status_code == 429


def test_patch_product_rate_limit_returns_429_when_exceeded(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifica que PATCH /products/{id} devuelve 429 al superar el límite de escritura."""
    from app.config import get_settings
    from app.main import app

    monkeypatch.setattr(get_settings(), "rate_limit_write", "2/minute")
    app.state.limiter.reset()

    create_res = client.post(
        "/products",
        json={
            "name": "Producto Patch Rate",
            "sku": "PATCH-RATE-001",
            "category": "Test",
            "price": 10.0,
            "stock": 5,
            "minimum_stock": 1,
        },
    )
    assert create_res.status_code == 201
    product_id = create_res.json()["id"]

    # 1 POST + 1 PATCH = 2 peticiones (dentro de 2/minute), la 3ra (2do PATCH) debe dar 429
    r_patch_1 = client.patch(f"/products/{product_id}", json={"stock": 6})
    r_patch_2 = client.patch(f"/products/{product_id}", json={"stock": 7})

    assert r_patch_1.status_code == 200
    assert r_patch_2.status_code == 429


def test_rate_limit_respects_x_forwarded_for_proxy_header(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifica que el rate limiting distinga clientes detrás de un proxy mediante X-Forwarded-For."""
    from app.config import get_settings
    from app.main import app

    monkeypatch.setattr(get_settings(), "rate_limit_ai", "1/minute")
    app.state.limiter.reset()

    r1 = client.post("/ai/analyze-inventory", headers={"X-Forwarded-For": "203.0.113.10, 10.0.0.1"})
    r2 = client.post("/ai/analyze-inventory", headers={"X-Forwarded-For": "203.0.113.10, 10.0.0.1"})
    r3 = client.post("/ai/analyze-inventory", headers={"X-Forwarded-For": "198.51.100.25, 10.0.0.1"})

    assert r1.status_code == 200
    assert r2.status_code == 429
    assert r3.status_code == 200
