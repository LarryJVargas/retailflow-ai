import json
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
import pytest

from app.config import get_settings


@pytest.fixture(autouse=True)
def configure_test_api_key():
    """Garantiza que para las pruebas donde se invoque el mock exista una API key configurada."""
    settings = get_settings()
    original_key = settings.gemini_api_key
    settings.gemini_api_key = "test-fake-key-for-mocking"
    yield
    settings.gemini_api_key = original_key


def test_ai_analyze_inventory_empty_db(client: TestClient) -> None:
    """Si no hay productos con stock bajo ni agotados, responde saludable sin llamar a la IA."""
    response = client.post("/ai/analyze-inventory")
    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "fallback"
    assert data["model_used"] is None
    assert data["total_critical_products"] == 0
    assert data["recommendations"] == []
    assert "saludables" in data["summary"].lower()


def test_ai_analyze_inventory_valid_gemini_response(client: TestClient) -> None:
    """Verifica que con respuesta válida y coherente de Gemini, la API responde con source='gemini'."""
    # Insertamos un producto agotado (stock=0, min=10 -> suggested=10) y uno bajo stock (stock=2, min=5 -> suggested=3)
    client.post(
        "/products",
        json={"name": "Camisa Denim", "sku": "SHIRT-001", "category": "Moda", "price": 40.0, "stock": 0, "minimum_stock": 10},
    )
    client.post(
        "/products",
        json={"name": "Jean Slim", "sku": "JEAN-001", "category": "Moda", "price": 60.0, "stock": 2, "minimum_stock": 5},
    )

    fake_gemini_payload = {
        "summary": "Se detectaron 2 artículos críticos con necesidad urgente de reaprovisionamiento.",
        "recommendations": [
            {
                "sku": "SHIRT-001",
                "explanation": "Artículo agotado con alta rotación estacional. Reponer urgentemente.",
                "priority": "CRITICAL",
                "suggested_quantity": 10,  # Coincide exactamente con el cálculo backend (10 - 0)
            },
            {
                "sku": "JEAN-001",
                "explanation": "Stock bajo por debajo del umbral de seguridad.",
                "priority": "HIGH",
                "suggested_quantity": 3,  # Coincide exactamente con el cálculo backend (5 - 2)
            },
        ],
    }

    mock_response = MagicMock()
    mock_response.text = json.dumps(fake_gemini_payload)

    with patch("google.genai.Client") as mock_client_cls:
        mock_instance = mock_client_cls.return_value
        mock_instance.models.generate_content.return_value = mock_response

        response = client.post("/ai/analyze-inventory")

    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "gemini"
    assert data["model_used"] == get_settings().gemini_model
    assert data["total_critical_products"] == 2
    assert len(data["recommendations"]) == 2

    rec_map = {r["sku"]: r for r in data["recommendations"]}
    assert rec_map["SHIRT-001"]["suggested_quantity"] == 10
    assert rec_map["SHIRT-001"]["priority"] == "CRITICAL"
    assert rec_map["JEAN-001"]["suggested_quantity"] == 3
    assert rec_map["JEAN-001"]["priority"] == "HIGH"


def test_ai_analyze_inventory_invalid_json_triggers_fallback(client: TestClient) -> None:
    """Si Gemini retorna un texto que no es JSON válido, el sistema responde con fallback determinista."""
    client.post(
        "/products",
        json={"name": "Zapatos Oxford", "sku": "SHOE-OXF-001", "category": "Calzado", "price": 90.0, "stock": 0, "minimum_stock": 8},
    )

    mock_response = MagicMock()
    mock_response.text = "Esto no es un JSON, es una respuesta rota de un modelo."

    with patch("google.genai.Client") as mock_client_cls:
        mock_instance = mock_client_cls.return_value
        mock_instance.models.generate_content.return_value = mock_response

        response = client.post("/ai/analyze-inventory")

    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "fallback"
    assert data["model_used"] is None
    assert data["total_critical_products"] == 1
    assert data["recommendations"][0]["sku"] == "SHOE-OXF-001"
    assert data["recommendations"][0]["suggested_quantity"] == 8
    assert data["recommendations"][0]["priority"] == "CRITICAL"


def test_ai_analyze_inventory_hallucinated_sku_triggers_fallback(client: TestClient) -> None:
    """Si Gemini alucina un SKU que no estaba en la lista provista, se activa el fallback de seguridad."""
    client.post(
        "/products",
        json={"name": "Bufanda Lana", "sku": "BUF-001", "category": "Accesorios", "price": 15.0, "stock": 1, "minimum_stock": 5},
    )

    fake_payload_with_hallucination = {
        "summary": "Recomendación con SKU inventado.",
        "recommendations": [
            {
                "sku": "SKU-INVENTADO-999",  # No existe en la base de datos
                "explanation": "Producto alucinado.",
                "priority": "HIGH",
                "suggested_quantity": 4,
            }
        ],
    }

    mock_response = MagicMock()
    mock_response.text = json.dumps(fake_payload_with_hallucination)

    with patch("google.genai.Client") as mock_client_cls:
        mock_instance = mock_client_cls.return_value
        mock_instance.models.generate_content.return_value = mock_response

        response = client.post("/ai/analyze-inventory")

    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "fallback"
    # Debe contener el SKU real, no el alucinado
    assert data["recommendations"][0]["sku"] == "BUF-001"
    assert data["recommendations"][0]["suggested_quantity"] == 4


def test_ai_analyze_inventory_inconsistent_quantity_triggers_fallback(client: TestClient) -> None:
    """Si Gemini propone una cantidad distinta a la calculada por las reglas del backend, se rechaza."""
    client.post(
        "/products",
        json={"name": "Gorra Sport", "sku": "CAP-002", "category": "Accesorios", "price": 12.0, "stock": 1, "minimum_stock": 10},
    )
    # Backend espera reposición = 10 - 1 = 9

    fake_payload_wrong_quantity = {
        "summary": "Recomendación con cantidad alterada.",
        "recommendations": [
            {
                "sku": "CAP-002",
                "explanation": "Sugerimos reponer mucho más de lo calculado.",
                "priority": "HIGH",
                "suggested_quantity": 50,  # Inconsistente con el backend (esperado 9)
            }
        ],
    }

    mock_response = MagicMock()
    mock_response.text = json.dumps(fake_payload_wrong_quantity)

    with patch("google.genai.Client") as mock_client_cls:
        mock_instance = mock_client_cls.return_value
        mock_instance.models.generate_content.return_value = mock_response

        response = client.post("/ai/analyze-inventory")

    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "fallback"
    assert data["recommendations"][0]["sku"] == "CAP-002"
    assert data["recommendations"][0]["suggested_quantity"] == 9  # Valor determinista respetado


def test_ai_analyze_inventory_api_exception_triggers_fallback(client: TestClient) -> None:
    """Si la API de Gemini arroja un error 429, timeout o caída de red, no se produce un HTTP 500."""
    client.post(
        "/products",
        json={"name": "Reloj Pulsera", "sku": "REL-001", "category": "Joyería", "price": 150.0, "stock": 0, "minimum_stock": 4},
    )

    with patch("google.genai.Client") as mock_client_cls:
        mock_instance = mock_client_cls.return_value
        mock_instance.models.generate_content.side_effect = TimeoutError("Gemini API connection timed out")

        response = client.post("/ai/analyze-inventory")

    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "fallback"
    assert data["total_critical_products"] == 1
    assert data["recommendations"][0]["sku"] == "REL-001"
    assert data["recommendations"][0]["suggested_quantity"] == 4


def test_ai_analyze_inventory_missing_api_key_triggers_fallback(client: TestClient) -> None:
    """Si GEMINI_API_KEY no está configurada, se utiliza el fallback sin intentar invocar el SDK."""
    settings = get_settings()
    settings.gemini_api_key = ""  # Vacía

    client.post(
        "/products",
        json={"name": "Lentes Sol", "sku": "LEN-001", "category": "Accesorios", "price": 30.0, "stock": 1, "minimum_stock": 6},
    )

    response = client.post("/ai/analyze-inventory")
    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "fallback"
    assert data["recommendations"][0]["sku"] == "LEN-001"
    assert data["recommendations"][0]["suggested_quantity"] == 5
