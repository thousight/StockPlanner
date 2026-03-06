import pytest
from decimal import Decimal
from datetime import datetime
from src.schemas.transactions import (
    TransactionCreate, 
    StockMetadata, 
    RealEstateMetadata, 
    FundMetadata, 
    MetalMetadata, 
    GenericMetadata
)
from pydantic import ValidationError

def test_stock_metadata_validation():
    data = {
        "asset_id": 1,
        "action": "BUY",
        "quantity": "10.0",
        "price_per_share": "100.0",
        "asset_metadata": {"type": "STOCK"}
    }
    tx = TransactionCreate(**data)
    assert isinstance(tx.asset_metadata, StockMetadata)
    assert tx.asset_metadata.type == "STOCK"

def test_real_estate_metadata_validation():
    data = {
        "asset_id": 2,
        "action": "BUY",
        "quantity": "1.0",
        "price_per_share": "500000.0",
        "asset_metadata": {
            "type": "REAL_ESTATE",
            "property_type": "apartment",
            "address": "123 Main St",
            "purchase_price": "500000.0"
        }
    }
    tx = TransactionCreate(**data)
    assert isinstance(tx.asset_metadata, RealEstateMetadata)
    assert tx.asset_metadata.property_type == "apartment"
    assert tx.asset_metadata.address == "123 Main St"
    assert tx.asset_metadata.purchase_price == Decimal("500000.0")

def test_fund_metadata_validation():
    data = {
        "asset_id": 3,
        "action": "BUY",
        "quantity": "1.0",
        "price_per_share": "10000.0",
        "asset_metadata": {
            "type": "FUND",
            "commitment_date": "2024-01-01T00:00:00",
            "vintage_year": 2024
        }
    }
    tx = TransactionCreate(**data)
    assert isinstance(tx.asset_metadata, FundMetadata)
    assert tx.asset_metadata.vintage_year == 2024
    assert isinstance(tx.asset_metadata.commitment_date, datetime)

def test_metal_metadata_validation():
    data = {
        "asset_id": 4,
        "action": "BUY",
        "quantity": "50.0",
        "price_per_share": "2000.0",
        "asset_metadata": {"type": "METAL"}
    }
    tx = TransactionCreate(**data)
    assert isinstance(tx.asset_metadata, MetalMetadata)

def test_generic_metadata_validation():
    data = {
        "asset_id": 5,
        "action": "BUY",
        "quantity": "1.0",
        "price_per_share": "100.0",
        "asset_metadata": {
            "type": "GENERIC",
            "description": "Custom asset"
        }
    }
    tx = TransactionCreate(**data)
    assert isinstance(tx.asset_metadata, GenericMetadata)
    assert tx.asset_metadata.description == "Custom asset"

def test_fractional_shares_validation():
    data = {
        "asset_id": 1,
        "action": "BUY",
        "quantity": "0.123456",
        "price_per_share": "150.75"
    }
    tx = TransactionCreate(**data)
    assert tx.quantity == Decimal("0.123456")
    assert tx.price_per_share == Decimal("150.75")

def test_currency_code_validation():
    # Valid currency
    tx = TransactionCreate(
        asset_id=1, action="BUY", quantity=Decimal("1"), price_per_share=Decimal("10"), currency="EUR"
    )
    assert tx.currency == "EUR"
    
    # Invalid currency (too short)
    with pytest.raises(ValidationError):
        TransactionCreate(
            asset_id=1, action="BUY", quantity=Decimal("1"), price_per_share=Decimal("10"), currency="US"
        )
    
    # Invalid currency (too long)
    with pytest.raises(ValidationError):
        TransactionCreate(
            asset_id=1, action="BUY", quantity=Decimal("1"), price_per_share=Decimal("10"), currency="USDOLLAR"
        )

def test_polymorphic_metadata_mismatch():
    # type "STOCK" but providing "REAL_ESTATE" fields should still work if discriminator is handled correctly,
    # but providing an unknown type should fail.
    data = {
        "asset_id": 1,
        "action": "BUY",
        "quantity": "10.0",
        "price_per_share": "100.0",
        "asset_metadata": {"type": "UNKNOWN"}
    }
    with pytest.raises(ValidationError):
        TransactionCreate(**data)
