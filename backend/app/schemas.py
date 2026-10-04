from datetime import date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class TransactionCreate(BaseModel):
    account_id: int = Field(
        default=1, description="Foreign key ID linking to the account"
    )
    amount: Decimal = Field(
        ..., gt=0, description="Amount must be greater than 0"
    )
    merchant: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Store or service name",
    )
    category: str = Field(
        ..., min_length=2, max_length=50, description="Spending category"
    )
    transaction_date: date = Field(..., description="Date of transaction")
    description: Optional[str] = Field(
        None, max_length=255, description="Optional notes"
    )


class TransactionResponse(BaseModel):
    id: int
    account_id: int
    amount: Decimal
    merchant: str
    category: str
    transaction_date: date
    description: Optional[str] = None

    class Config:
        from_attributes = True