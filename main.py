import logging
from datetime import UTC, datetime

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from database.session import create_db_and_tables, get_session
from models.product import (
    Product,
    ProductCreate,
    ProductUpdate,
    StockAdjustment,
    Supplier,
    SupplierCreate,
)

# ============================================================
# Logging
# ============================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# FastAPI App
# ============================================================

app = FastAPI(title="TechVault Inventory API", version="2.0.0")
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)
# ============================================================
# Startup
# ============================================================


@app.on_event("startup")
def startup():
    create_db_and_tables()


# ============================================================
# Global Exception Handlers
# ============================================================


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(exc.detail)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "status_code": exc.status_code,
            "message": exc.detail,
            "path": request.url.path,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):

    errors = []

    for error in exc.errors():
        errors.append(
            {
                "field": ".".join(str(x) for x in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
        )

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "status_code": 422,
            "message": "Validation error",
            "errors": errors,
            "path": request.url.path,
        },
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):

    logger.error(str(exc))

    return JSONResponse(
        status_code=409,
        content={
            "success": False,
            "status_code": 409,
            "message": "Duplicate entry or constraint violation",
            "path": request.url.path,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):

    logger.error(str(exc))

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "status_code": 500,
            "message": "Internal server error",
            "path": request.url.path,
        },
    )


# ============================================================
# SUPPLIER CRUD
# ============================================================


@app.post("/suppliers", response_model=Supplier, status_code=201)
def create_supplier(
    supplier: SupplierCreate,
    session: Session = Depends(get_session),
):
    existing = session.exec(
        select(Supplier).where(Supplier.email == supplier.email)
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Supplier already exists",
        )

    db_supplier = Supplier(**supplier.model_dump())

    session.add(db_supplier)
    session.commit()
    session.refresh(db_supplier)

    return db_supplier


@app.get("/suppliers", response_model=list[Supplier])
def list_suppliers(
    session: Session = Depends(get_session),
):
    return session.exec(select(Supplier)).all()


@app.get("/suppliers/{supplier_id}", response_model=Supplier)
def get_supplier(
    supplier_id: int,
    session: Session = Depends(get_session),
):
    supplier = session.get(Supplier, supplier_id)

    if not supplier:
        raise HTTPException(
            status_code=404,
            detail="Supplier not found",
        )

    return supplier


# ============================================================
# PRODUCT CRUD
# ============================================================


@app.post("/products", response_model=Product, status_code=201)
def create_product(
    product: ProductCreate,
    session: Session = Depends(get_session),
):
    if product.supplier_id is not None:
        supplier = session.get(Supplier, product.supplier_id)

        if not supplier:
            raise HTTPException(
                status_code=404,
                detail="Supplier not found",
            )

    db_product = Product(**product.model_dump())

    session.add(db_product)
    session.commit()
    session.refresh(db_product)

    return db_product


@app.get("/products", response_model=list[Product])
def list_products(
    session: Session = Depends(get_session),
):
    return session.exec(select(Product)).all()


@app.get("/products/{product_id}", response_model=Product)
def get_product(
    product_id: int,
    session: Session = Depends(get_session),
):
    product = session.get(Product, product_id)

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return product


@app.patch("/products/bulk-update")
def bulk_update_price(
    category: str, discount_percent: float, session: Session = Depends(get_session)
):

    # Validate discount
    if discount_percent < 0 or discount_percent > 100:
        raise HTTPException(
            status_code=400, detail="Discount must be between 0 and 100 percent"
        )

    # Find products in category
    products = session.exec(select(Product).where(Product.category == category)).all()

    if not products:
        raise HTTPException(
            status_code=404, detail="No products found in this category"
        )

    updated_products = 0

    for product in products:

        new_price = product.price * (1 - discount_percent / 100)

        # Minimum price rule
        if new_price < 100:
            raise HTTPException(
                status_code=400,
                detail=f"{product.name} price would fall below minimum price",
            )

        product.price = round(new_price, 2)
        product.updated_at = datetime.utcnow()

        session.add(product)

        updated_products += 1

    session.commit()

    return {
        "message": "Bulk price update successful",
        "category": category,
        "discount_percent": discount_percent,
        "products_updated": updated_products,
    }


@app.patch("/products/{product_id}", response_model=Product)
def update_product(
    product_id: int,
    product_update: ProductUpdate,
    session: Session = Depends(get_session),
):
    product = session.get(Product, product_id)

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    for key, value in product_update.model_dump(exclude_unset=True).items():
        setattr(product, key, value)

    product.updated_at = datetime.utcnow()

    session.add(product)
    session.commit()
    session.refresh(product)

    return product


@app.delete("/products/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    session: Session = Depends(get_session),
):
    product = session.get(Product, product_id)

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    session.delete(product)
    session.commit()


# ============================================================
# STOCK ADJUSTMENT
# ============================================================


@app.patch("/products/adjust-stock")
def adjust_stock(
    adjustments: list[StockAdjustment], session: Session = Depends(get_session)
):

    successful = []
    failed = []

    for adjustment in adjustments:

        product = session.get(Product, adjustment.product_id)

        if not product:
            failed.append(
                {"product_id": adjustment.product_id, "message": "Product not found"}
            )
            continue

        new_stock = product.stock + adjustment.quantity_to_add

        if new_stock > 5000:
            failed.append(
                {
                    "product_id": adjustment.product_id,
                    "message": "Stock cannot exceed 5000",
                }
            )
            continue

        product.stock = new_stock
        product.updated_at = datetime.utcnow()

        session.add(product)

        successful.append({"product_id": adjustment.product_id, "new_stock": new_stock})

    session.commit()

    return {
        "message": "Stock adjustment completed",
        "successful_updates": successful,
        "failed_updates": failed,
    }


# ============================================================
# GLOBAL ERROR HANDLERS
# ============================================================


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": True,
            "status_code": 404,
            "message": "Resource not found",
            "errors": [],
            "timestamp": datetime.now(UTC).isoformat(),
            "path": request.url.path,
        },
    )
