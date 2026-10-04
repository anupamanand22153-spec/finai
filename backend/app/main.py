from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from backend.app.database import get_db, engine, Base
from backend.app.models import Transaction, Budget
from backend.app.schemas import (
    TransactionCreate,
    TransactionResponse,
    TransactionListResponse,
    BudgetCreate,
    BudgetResponse,
)

app = FastAPI(title="FinAI API", version="0.1.0")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "FinAI API"}

# --- Transactions Endpoints ---
@app.post("/transactions", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(txn: TransactionCreate, db: AsyncSession = Depends(get_db)):
    new_txn = Transaction(**txn.model_dump())
    db.add(new_txn)
    await db.commit()
    await db.refresh(new_txn)
    return new_txn

@app.get("/transactions", response_model=TransactionListResponse)
async def get_transactions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Transaction).order_by(Transaction.id.desc()))
    transactions = result.scalars().all()
    return {"count": len(transactions), "transactions": transactions}

# --- Budgets Endpoints ---
@app.post("/budgets", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
async def create_budget(budget: BudgetCreate, db: AsyncSession = Depends(get_db)):
    new_budget = Budget(**budget.model_dump())
    db.add(new_budget)
    await db.commit()
    await db.refresh(new_budget)
    return new_budget

@app.get("/budgets", response_model=List[BudgetResponse])
async def get_budgets(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Budget).order_by(Budget.id.desc()))
    return result.scalars().all()