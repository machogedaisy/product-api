def test_full_product_flow(client):
    """Test the full product flow from supplier creation to deletion."""

    # 1. Create a supplier
    supplier_data = {
        "name": "Integration Supplier",
        "contact_person": "John Doe",
        "email": "integration@example.com",
        "phone": "0712345678",
        "is_active": True,
    }

    supplier_response = client.post("/suppliers", json=supplier_data)

    assert supplier_response.status_code == 201

    supplier_id = supplier_response.json()["id"]

    # 2. Create a product
    product_data = {
        "name": "Integration Product",
        "description": "Product for integration testing",
        "brand": "HP",
        "category": "Laptops",
        "price": 199.99,
        "stock": 10,
        "warranty_months": 12,
        "sku": "LAP-HP-0001",
        "supplier_id": supplier_id,
    }

    product_response = client.post("/products", json=product_data)

    assert product_response.status_code == 201

    product_id = product_response.json()["id"]

    # 3. Get the product
    get_response = client.get(f"/products/{product_id}")

    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Integration Product"

    # 4. Update the product
    update_data = {
        "name": "Updated Integration Product",
        "price": 249.99,
    }

    update_response = client.patch(
        f"/products/{product_id}",
        json=update_data,
    )

    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Integration Product"
    assert update_response.json()["price"] == 249.99

    # 5. Delete the product
    delete_response = client.delete(f"/products/{product_id}")

    assert delete_response.status_code == 204

    # 6. Verify deletion
    verify_response = client.get(f"/products/{product_id}")

    assert verify_response.status_code == 404
