import re
from datetime import datetime

from pydantic import field_validator
from sqlmodel import Field, SQLModel

# ============================================================
# Supplier Model
# ============================================================


class Supplier(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    contact_person: str
    email: str = Field(unique=True)
    phone: str
    is_active: bool = True


# ============================================================
# Product Model
# ============================================================


class Product(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    name: str = Field(index=True)
    description: str

    brand: str = Field(index=True)

    category: str = Field(index=True)

    price: float = Field(gt=0)

    stock: int = Field(ge=0)

    warranty_months: int = Field(ge=0)

    sku: str = Field(unique=True, index=True)

    supplier_id: int | None = Field(default=None, foreign_key="supplier.id")

    created_at: datetime = Field(default_factory=datetime.utcnow)

    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================
# Product Create Model
# ============================================================


class ProductCreate(SQLModel):
    name: str
    description: str
    brand: str
    category: str
    price: float = Field(gt=0)
    stock: int = Field(ge=0)
    warranty_months: int = Field(ge=0)
    sku: str
    supplier_id: int | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")

        if not v[0].isupper():
            raise ValueError("Name must start with a capital letter")

        if re.search(r"[^a-zA-Z0-9\s\-]", v):
            raise ValueError("Name cannot contain special characters")

        return v

    @field_validator("brand")
    @classmethod
    def validate_brand(cls, v):
        allowed = [
            "HP",
            "Dell",
            "Lenovo",
            "Apple",
            "Samsung",
            "Intel",
            "AMD",
            "Corsair",
            "Logitech",
            "Other",
        ]

        for brand in allowed:
            if v.lower() == brand.lower():
                return brand

        raise ValueError("Invalid brand")

    @field_validator("category")
    @classmethod
    def validate_category(cls, v):
        allowed = [
            "Laptops",
            "Monitors",
            "Storage",
            "Processors",
            "Memory",
            "Keyboards",
            "Mice",
            "Accessories",
        ]

        for category in allowed:
            if v.lower() == category.lower():
                return category

        raise ValueError("Invalid category")

    @field_validator("price")
    @classmethod
    def validate_price(cls, v):
        if round(v, 2) != v:
            raise ValueError("Price must have at most 2 decimal places")

        if v < 100:
            raise ValueError("Minimum price is 100")

        if v > 500000:
            raise ValueError("Maximum price is 500000")

        return round(v, 2)

    @field_validator("sku")
    @classmethod
    def validate_sku(cls, v):
        pattern = r"^[A-Z]{3,4}-[A-Z]{2,4}-[0-9]{4}$"

        if not re.match(pattern, v):
            raise ValueError("SKU must follow CAT-BRAND-0000 format")

        valid_prefixes = ["LAP", "MON", "STO", "PRO", "MEM", "KEY", "MOU", "ACC"]

        prefix = v.split("-")[0]

        if prefix not in valid_prefixes:
            raise ValueError("Invalid category abbreviation")

        return v

    @field_validator("warranty_months")
    @classmethod
    def validate_warranty(cls, v):
        if v < 0 or v > 36:
            raise ValueError("Warranty must be between 0 and 36 months")

        return v


# ============================================================
# Product Update Model
# ============================================================


class ProductUpdate(SQLModel):
    name: str | None = None
    description: str | None = None
    brand: str | None = None
    category: str | None = None
    price: float | None = None
    stock: int | None = None
    warranty_months: int | None = None
    sku: str | None = None
    supplier_id: int | None = None


# ============================================================
# Supplier Create Model
# ============================================================

# ============================================================
# Supplier Create Model
# ============================================================


class SupplierCreate(SQLModel):

    name: str
    contact_person: str
    email: str
    phone: str
    is_active: bool = True

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):

        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

        if not re.match(pattern, v):
            raise ValueError("Invalid email address")

        return v.lower()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):

        if not v.isdigit():
            raise ValueError("Phone number must contain digits only")

        if len(v) < 10:
            raise ValueError("Phone number must be at least 10 digits")

        return v

    # ============================================================


# Stock Adjustment Model
# ============================================================


class StockAdjustment(SQLModel):
    product_id: int
    quantity_to_add: int = Field(gt=0)
