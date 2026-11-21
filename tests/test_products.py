from fastapi.testclient import TestClient


def test_create_product_success(client: TestClient) -> None:
    payload = {
        "name": "Zapatillas Urbanas Negras",
        "sku": "SHOE-BLK-001",
        "category": "Calzado",
        "price": 89.99,
        "stock": 25,
        "minimum_stock": 5,
    }
    response = client.post("/products", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["id"] is not None
    assert data["name"] == payload["name"]
    assert data["sku"] == payload["sku"]
    assert data["category"] == payload["category"]
    assert data["price"] == payload["price"]
    assert data["stock"] == payload["stock"]
    assert data["minimum_stock"] == payload["minimum_stock"]
    assert "created_at" in data


def test_create_product_with_duplicate_sku_returns_409(client: TestClient) -> None:
    payload = {
        "name": "Mochila Impermeable",
        "sku": "BAG-WTP-001",
        "category": "Accesorios",
        "price": 45.0,
        "stock": 10,
        "minimum_stock": 2,
    }
    # Primera creación exitosa
    r1 = client.post("/products", json=payload)
    assert r1.status_code == 201

    # Segunda creación con mismo SKU debe fallar con 409
    r2 = client.post("/products", json=payload)
    assert r2.status_code == 409
    assert "already exists" in r2.json()["detail"] or "Ya existe" in r2.json()["detail"]


def test_create_product_negative_price_fails_with_422(client: TestClient) -> None:
    payload = {
        "name": "Producto Precio Negativo",
        "sku": "INV-NEG-001",
        "category": "General",
        "price": -10.5,
        "stock": 5,
        "minimum_stock": 1,
    }
    response = client.post("/products", json=payload)
    assert response.status_code == 422


def test_create_product_negative_stock_fails_with_422(client: TestClient) -> None:
    payload = {
        "name": "Producto Stock Negativo",
        "sku": "INV-NEG-002",
        "category": "General",
        "price": 19.99,
        "stock": -1,
        "minimum_stock": 1,
    }
    response = client.post("/products", json=payload)
    assert response.status_code == 422


def test_list_products(client: TestClient) -> None:
    # Inicialmente vacía
    res_empty = client.get("/products")
    assert res_empty.status_code == 200
    assert res_empty.json() == []

    # Insertamos dos productos
    p1 = {"name": "Prod 1", "sku": "SKU-001", "category": "A", "price": 10.0, "stock": 5, "minimum_stock": 1}
    p2 = {"name": "Prod 2", "sku": "SKU-002", "category": "B", "price": 20.0, "stock": 15, "minimum_stock": 2}
    client.post("/products", json=p1)
    client.post("/products", json=p2)

    res_list = client.get("/products")
    assert res_list.status_code == 200
    data = res_list.json()
    assert len(data) == 2
    assert data[0]["sku"] == "SKU-001"
    assert data[1]["sku"] == "SKU-002"


def test_get_product_by_id_success(client: TestClient) -> None:
    payload = {"name": "Gorra Deportiva", "sku": "CAP-001", "category": "Accesorios", "price": 15.0, "stock": 30, "minimum_stock": 5}
    created = client.post("/products", json=payload).json()

    response = client.get(f"/products/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]
    assert response.json()["sku"] == "CAP-001"


def test_get_product_by_id_not_found(client: TestClient) -> None:
    response = client.get("/products/99999")
    assert response.status_code == 404
    assert "no encontrado" in response.json()["detail"].lower() or "not found" in response.json()["detail"].lower()


def test_patch_product_success(client: TestClient) -> None:
    payload = {"name": "Campera Cuero", "sku": "JKT-001", "category": "Indumentaria", "price": 120.0, "stock": 10, "minimum_stock": 2}
    created = client.post("/products", json=payload).json()

    update_payload = {"price": 139.99, "stock": 8}
    response = client.patch(f"/products/{created['id']}", json=update_payload)
    assert response.status_code == 200
    updated = response.json()
    assert updated["price"] == 139.99
    assert updated["stock"] == 8
    assert updated["name"] == "Campera Cuero"  # Se mantiene intacto


def test_patch_product_duplicate_sku_returns_409(client: TestClient) -> None:
    p1 = client.post("/products", json={"name": "P1", "sku": "SKU-AAA", "category": "A", "price": 10.0, "stock": 1, "minimum_stock": 0}).json()
    p2 = client.post("/products", json={"name": "P2", "sku": "SKU-BBB", "category": "A", "price": 10.0, "stock": 1, "minimum_stock": 0}).json()

    # Intentar cambiar el SKU de p2 al SKU de p1
    response = client.patch(f"/products/{p2['id']}", json={"sku": "SKU-AAA"})
    assert response.status_code == 409


def test_patch_product_not_found(client: TestClient) -> None:
    response = client.patch("/products/99999", json={"name": "Inexistente"})
    assert response.status_code == 404


def test_delete_product_success(client: TestClient) -> None:
    payload = {"name": "Para Borrar", "sku": "DEL-001", "category": "Test", "price": 5.0, "stock": 2, "minimum_stock": 0}
    created = client.post("/products", json=payload).json()

    # Eliminar
    delete_res = client.delete(f"/products/{created['id']}")
    assert delete_res.status_code == 204

    # Verificar que ya no existe
    get_res = client.get(f"/products/{created['id']}")
    assert get_res.status_code == 404


def test_delete_product_not_found(client: TestClient) -> None:
    response = client.delete("/products/99999")
    assert response.status_code == 404
