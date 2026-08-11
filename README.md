# TechVault Product Inventory API

## Description
TechVault Inventory API is a FastAPI backend system for managing electronics products, suppliers, and stock operations.

The API provides product CRUD operations, validation, error handling, supplier management, bulk price updates, and stock adjustments.

## Technologies Used

- Python
- FastAPI
- SQLModel
- PostgreSQL
- Docker
- Alembic
- Pydantic

## Features

### Product Management
- Create products
- View products
- Update products
- Delete products
- Search products

### Validation
- Product name validation
- Brand standardization
- Category validation
- Price validation
- Stock validation
- SKU format validation
- Warranty validation

### Supplier Management
- Add suppliers
- Validate supplier email
- Validate phone numbers
- Link suppliers to products

### Inventory Operations
- Bulk price updates
- Stock adjustments
- Database integrity checks

### Error Handling
The API uses standardized error responses containing:

- success status
- status code
- message
- errors
- timestamp
- request path


## Running the Project

### Start PostgreSQL Database

```bash
docker compose up -d

PROJECT STRUCTURE
product-api/
│
├── main.py
├── models/
│   └── product.py
├── database/
│   └── session.py
├── screenshots/
├── docker-compose.yml
├── README.md
└── pyproject.toml

SWAGGER UI
http://127.0.0.1:8000/docs

AUTHOR
DAISY MOKEIRA

Lab 11 conditional workflow test