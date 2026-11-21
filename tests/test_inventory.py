import csv
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.report_service import save_inventory_report_to_disk


def test_inventory_empty_database(client: TestClient) -> None:
    # 1. Summary vacío
    res_summary = client.get("/inventory/summary")
    assert res_summary.status_code == 200
    assert res_summary.json() == {
        "total_products": 0,
        "low_stock_products": 0,
        "out_of_stock_products": 0,
        "healthy_products": 0,
    }

    # 2. Low stock vacío
    res_low = client.get("/inventory/low-stock")
    assert res_low.status_code == 200
    assert res_low.json() == []

    # 3. Out of stock vacío
    res_out = client.get("/inventory/out-of-stock")
    assert res_out.status_code == 200
    assert res_out.json() == []

    # 4. Reporte CSV vacío (solo encabezados)
    res_report = client.get("/inventory/report")
    assert res_report.status_code == 200
    assert "text/csv" in res_report.headers["content-type"]
    lines = res_report.text.strip().split("\n")
    assert len(lines) == 1
    assert "SKU,Nombre,Categoría,Stock Actual,Stock Mínimo,Estado,Reposición Sugerida" in lines[0]


def test_inventory_classification_and_metrics(client: TestClient) -> None:
    # 1. Producto con stock bajo (stock > 0 y stock < minimum_stock)
    p_low = {
        "name": "Buzo Hoodie Negro",
        "sku": "BUZ-BLK-001",
        "category": "Indumentaria",
        "price": 45.0,
        "stock": 3,
        "minimum_stock": 10,
    }
    # 2. Producto agotado con minimum_stock > 0 (stock == 0)
    p_out = {
        "name": "Gorra Trucker",
        "sku": "CAP-TRK-001",
        "category": "Accesorios",
        "price": 18.0,
        "stock": 0,
        "minimum_stock": 15,
    }
    # 3. Producto saludable (stock >= minimum_stock y stock > 0)
    p_healthy = {
        "name": "Remera Lisa",
        "sku": "REM-LIS-001",
        "category": "Indumentaria",
        "price": 20.0,
        "stock": 25,
        "minimum_stock": 10,
    }
    # 4. Caso borde: minimum_stock == 0 y stock > 0 -> Debe ser Healthy
    p_zero_min_healthy = {
        "name": "Sticker Pack",
        "sku": "STK-PCK-001",
        "category": "Merchandising",
        "price": 2.5,
        "stock": 50,
        "minimum_stock": 0,
    }
    # 5. Caso borde: minimum_stock == 0 y stock == 0 -> Debe ser Out of Stock
    p_zero_min_out = {
        "name": "Pines Metálicos",
        "sku": "PIN-MET-001",
        "category": "Merchandising",
        "price": 4.0,
        "stock": 0,
        "minimum_stock": 0,
    }

    for prod in [p_low, p_out, p_healthy, p_zero_min_healthy, p_zero_min_out]:
        res = client.post("/products", json=prod)
        assert res.status_code == 201

    # Verificar /inventory/summary: Partición mutuamente excluyente
    res_summary = client.get("/inventory/summary")
    assert res_summary.status_code == 200
    summary = res_summary.json()
    assert summary["total_products"] == 5
    assert summary["low_stock_products"] == 1
    assert summary["out_of_stock_products"] == 2
    assert summary["healthy_products"] == 2
    assert summary["total_products"] == (
        summary["low_stock_products"] + summary["out_of_stock_products"] + summary["healthy_products"]
    )

    # Verificar /inventory/low-stock
    res_low = client.get("/inventory/low-stock")
    assert res_low.status_code == 200
    low_items = res_low.json()
    assert len(low_items) == 1
    assert low_items[0]["sku"] == "BUZ-BLK-001"
    assert low_items[0]["stock"] == 3
    assert low_items[0]["suggested_restock"] == 7
    assert low_items[0]["status"] == "LOW_STOCK"

    # Verificar /inventory/out-of-stock
    res_out = client.get("/inventory/out-of-stock")
    assert res_out.status_code == 200
    out_items = res_out.json()
    assert len(out_items) == 2
    out_skus = {item["sku"]: item for item in out_items}

    # Producto con minimum_stock > 0
    assert "CAP-TRK-001" in out_skus
    assert out_skus["CAP-TRK-001"]["stock"] == 0
    assert out_skus["CAP-TRK-001"]["suggested_restock"] == 15
    assert out_skus["CAP-TRK-001"]["status"] == "OUT_OF_STOCK"

    # Producto con minimum_stock == 0
    assert "PIN-MET-001" in out_skus
    assert out_skus["PIN-MET-001"]["stock"] == 0
    assert out_skus["PIN-MET-001"]["suggested_restock"] == 0
    assert out_skus["PIN-MET-001"]["status"] == "OUT_OF_STOCK"


def test_inventory_csv_report_endpoint(client: TestClient) -> None:
    # Insertamos un producto agotado y uno con stock bajo
    client.post(
        "/products",
        json={"name": "Mochila", "sku": "MC-001", "category": "Bolsos", "price": 50.0, "stock": 0, "minimum_stock": 10},
    )
    client.post(
        "/products",
        json={"name": "Billetera", "sku": "BL-001", "category": "Bolsos", "price": 20.0, "stock": 2, "minimum_stock": 5},
    )
    # Uno saludable que NO debe aparecer en el reporte
    client.post(
        "/products",
        json={"name": "Cinturon", "sku": "CN-001", "category": "Bolsos", "price": 15.0, "stock": 30, "minimum_stock": 5},
    )

    response = client.get("/inventory/report")
    assert response.status_code == 200
    assert "attachment; filename=" in response.headers["content-disposition"]
    assert "inventory_report_" in response.headers["content-disposition"]

    # Parsear CSV recibido
    csv_reader = csv.reader(response.text.strip().split("\n"))
    rows = list(csv_reader)
    assert len(rows) == 3  # Header + 2 productos críticos

    header = rows[0]
    assert header == ["SKU", "Nombre", "Categoría", "Stock Actual", "Stock Mínimo", "Estado", "Reposición Sugerida"]

    skus_in_report = [row[0] for row in rows[1:]]
    assert "MC-001" in skus_in_report
    assert "BL-001" in skus_in_report
    assert "CN-001" not in skus_in_report


def test_save_inventory_report_to_disk_service(db_session: Session, tmp_path: Path) -> None:
    # Validamos que el servicio de guardado a disco escribe correctamente un archivo CSV
    output_dir = tmp_path / "test_reports"
    file_path = save_inventory_report_to_disk(db_session, output_dir=str(output_dir))

    assert Path(file_path).exists()
    content = Path(file_path).read_text(encoding="utf-8")
    assert "SKU,Nombre,Categoría,Stock Actual,Stock Mínimo,Estado,Reposición Sugerida" in content
