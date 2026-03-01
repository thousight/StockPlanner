from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Union, Literal
from decimal import Decimal
from datetime import datetime
from enum import Enum

class AssetType(str, Enum):
    STOCK = "STOCK"
    REAL_ESTATE = "REAL_ESTATE"
    FUND = "FUND"
    METAL = "METAL"
    GENERIC = "GENERIC"

class StockMetadata(BaseModel):
    type: Literal["STOCK"] = "STOCK"

class RealEstateMetadata(BaseModel):
    type: Literal["REAL_ESTATE"] = "REAL_ESTATE"
    property_type: str = Field(..., description="house, apartment, office, etc.")
    address: str
    purchase_price: Decimal

class FundMetadata(BaseModel):
    type: Literal["FUND"] = "FUND"
    commitment_date: datetime
    vintage_year: int

class MetalMetadata(BaseModel):
    type: Literal["METAL"] = "METAL"

class GenericMetadata(BaseModel):
    type: Literal["GENERIC"] = "GENERIC"
    description: Optional[str] = None

AssetMetadata = Union[
    StockMetadata,
    RealEstateMetadata,
    FundMetadata,
    MetalMetadata,
    GenericMetadata
]

class TransactionAction(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class TransactionBase(BaseModel):
    asset_id: int
    action: TransactionAction
    quantity: Decimal
    price_per_share: Decimal
    commission: Decimal = Decimal("0.0")
    tax: Decimal = Decimal("0.0")
    currency: str = Field("USD", min_length=3, max_length=3)
    fx_rate: Decimal = Decimal("1.0")
    date: Optional[datetime] = None
    asset_metadata: Optional[AssetMetadata] = Field(None, discriminator="type")

class TransactionCreate(TransactionBase):
    pass

class TransactionRead(TransactionBase):
    id: int
    user_id: str
    price_base: Decimal
    total_base: Decimal
    is_deleted: bool
    
    model_config = ConfigDict(from_attributes=True)
