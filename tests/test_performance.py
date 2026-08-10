import pytest


@pytest.mark.benchmark
def test_create_product_performance(client, benchmark):
    """Benchmark product creation performance."""

    product_data = {
        "name": "Performance Test Product",
        "description": "This is a test product for performance testing",
        "brand": "HP",
        "category": "Laptops",
        "price": 199.99,
        "stock": 10,
        "warranty_months": 12,
        "sku": "LAP-HP-0002",
    }

    def create_product():
        client.post("/products", json=product_data)

    benchmark(create_product)
