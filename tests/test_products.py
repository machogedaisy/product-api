def product_data(sku="LAP-HP-0001"):
    return {
        "name": "Test Product",
        "description": "This is a test product",
        "brand": "HP",
        "category": "Laptops",
        "price": 199.99,
        "stock": 10,
        "warranty_months": 12,
        "sku": sku,
    }


def test_create_product(client):
    response = client.post("/products", json=product_data())

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Test Product"
    assert data["brand"] == "HP"
    assert data["category"] == "Laptops"
    assert data["price"] == 199.99
    assert data["stock"] == 10


def test_list_products(client):
    client.post("/products", json=product_data())

    response = client.get("/products")

    assert response.status_code == 200

    data = response.json()

    assert len(data) >= 1
    assert data[0]["name"] == "Test Product"


def test_get_product(client):
    create_response = client.post("/products", json=product_data())

    product_id = create_response.json()["id"]

    response = client.get(f"/products/{product_id}")

    assert response.status_code == 200
    assert response.json()["name"] == "Test Product"


def test_get_product_not_found(client):
    response = client.get("/products/99999")

    assert response.status_code == 404


def test_update_product(client):
    create_response = client.post("/products", json=product_data())

    product_id = create_response.json()["id"]

    update_data = {"name": "Updated Product", "price": 299.99}

    response = client.patch(f"/products/{product_id}", json=update_data)

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Updated Product"
    assert data["price"] == 299.99


def test_delete_product(client):
    create_response = client.post("/products", json=product_data())

    product_id = create_response.json()["id"]

    response = client.delete(f"/products/{product_id}")

    assert response.status_code == 204

    response = client.get(f"/products/{product_id}")

    assert response.status_code == 404
