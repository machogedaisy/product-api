def test_404_error(client):
    """Test 404 error handling."""

    response = client.get("/non-existent-endpoint")

    assert response.status_code == 404

    data = response.json()

    assert data["error"] is True
    assert "message" in data


def test_product_not_found(client):
    """Test requesting a product that does not exist."""

    response = client.get("/products/99999")

    assert response.status_code == 404

    data = response.json()

    assert data["error"] is True
    assert "message" in data


def test_invalid_product_data(client):
    """Test validation with invalid product data."""

    product_data = {
        "name": "",
        "description": "Invalid product",
        "brand": "HP",
        "category": "Laptops",
        "price": -10,
        "stock": -5,
        "warranty_months": -1,
        "sku": "INVALID",
    }

    response = client.post("/products", json=product_data)

    assert response.status_code in [400, 422]


def test_missing_required_fields(client):
    """Test validation when required fields are missing."""

    product_data = {"name": "Incomplete Product"}

    response = client.post("/products", json=product_data)

    assert response.status_code == 422
