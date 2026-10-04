from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import List

class TransactionCreate(BaseModel):
    account_id: int
    amount: float = Field(..., gt=0, description="Amount must be strictly positive")
    merchant: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., min_length=1, max_length=50)
    transaction_date: date

class TransactionResponse(BaseModel):
    id: int
    account_id: int
    amount: float
    merchant: str
    category: str
    transaction_date: date
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

class TransactionListResponse(BaseModel):
    count: int
    transactions: List[TransactionResponse]

# --- Budget Schemas ---
class BudgetCreate(BaseModel):
    account_id: int
    category: str = Field(..., min_length=1, max_length=50)
    monthly_limit: float = Field(..., gt=0, description="Budget limit must be positive")
    month_year: str = Field(..., pattern=r"^\d{4}-(0[1-9]|1[0-2])$", description="Format: YYYY-MM")

class BudgetResponse(BaseModel):
    id: int
    account_id: int
    category: str
    monthly_limit: float
    month_year: str
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)



    # --- Analytics Schemas ---
class SpendSummaryResponse(BaseModel):
    total_spent: float
    transaction_count: int
    average_transaction: float

class CategoryBreakdownItem(BaseModel):
    category: str
    total_spent: float
    percentage: float
    count: int

class MerchantSpendItem(BaseModel):
    merchant: str
    total_spent: float
    count: int