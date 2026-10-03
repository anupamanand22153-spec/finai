from datetime import date
from pydantic import BaseModel, Field


class TransactionCreate(BaseModel):
    amount: float = Field(
        ..., gt=0, description="Transaction amount must be strictly positive"
    )
    merchant: str = Field(
        ..., min_length=2, max_length=100, description="Merchant name"
    )
    category: str = Field(..., description="Spending category (e.g. Food, Shopping)")
    transaction_date: date = Field(..., description="Date of the transaction")
    description: str | None = Field(
        default=None, description="Optional extra note"
    )