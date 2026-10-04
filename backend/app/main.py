import os
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from sqlalchemy import select, func, desc



from backend.app.database import get_db, engine, Base
from backend.app.models import Transaction, Budget
from backend.app.schemas import (
    TransactionCreate,
    TransactionResponse,
    TransactionListResponse,
    BudgetCreate,
    BudgetResponse,
)
from backend.app.schemas import (
    TransactionCreate,
    TransactionResponse,
    TransactionListResponse,
    BudgetCreate,
    BudgetResponse,
    SpendSummaryResponse,
    CategoryBreakdownItem,
    MerchantSpendItem,
)

app = FastAPI(title="FinAI API", version="0.1.0")

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    """Serve the interactive FinAI testing and operations dashboard."""
    try:
        return templates.TemplateResponse(request=request, name="index.html")
    except TypeError:
        return templates.TemplateResponse("index.html", {"request": request})

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




# --- Analytics Endpoints ---
@app.get("/analytics/summary", response_model=SpendSummaryResponse)
async def get_spend_summary(db: AsyncSession = Depends(get_db)):
    """Compute overall spend volume, average transaction amount, and total count."""
    query = select(
        func.coalesce(func.sum(Transaction.amount), 0.0).label("total_spent"),
        func.count(Transaction.id).label("transaction_count"),
        func.coalesce(func.avg(Transaction.amount), 0.0).label("average_transaction")
    )
    result = await db.execute(query)
    row = result.one()
    return {
        "total_spent": round(float(row.total_spent), 2),
        "transaction_count": int(row.transaction_count),
        "average_transaction": round(float(row.average_transaction), 2),
    }

@app.get("/analytics/categories", response_model=List[CategoryBreakdownItem])
async def get_category_breakdown(db: AsyncSession = Depends(get_db)):
    """Aggregate spending by category with percentages."""
    # First get total spend
    total_query = select(func.coalesce(func.sum(Transaction.amount), 0.0))
    total_res = await db.execute(total_query)
    total_spent = float(total_res.scalar() or 0.0)

    # Group by category
    query = (
        select(
            Transaction.category,
            func.sum(Transaction.amount).label("category_spent"),
            func.count(Transaction.id).label("count")
        )
        .group_by(Transaction.category)
        .order_by(desc("category_spent"))
    )
    result = await db.execute(query)
    rows = result.all()

    breakdown = []
    for r in rows:
        cat_spent = float(r.category_spent)
        pct = (cat_spent / total_spent * 100.0) if total_spent > 0 else 0.0
        breakdown.append({
            "category": r.category,
            "total_spent": round(cat_spent, 2),
            "percentage": round(pct, 2),
            "count": int(r.count)
        })
    return breakdown

@app.get("/analytics/merchants", response_model=List[MerchantSpendItem])
async def get_top_merchants(limit: int = 5, db: AsyncSession = Depends(get_db)):
    """Retrieve top merchants ranked by total spend."""
    query = (
        select(
            Transaction.merchant,
            func.sum(Transaction.amount).label("total_spent"),
            func.count(Transaction.id).label("count")
        )
        .group_by(Transaction.merchant)
        .order_by(desc("total_spent"))
        .limit(limit)
    )
    result = await db.execute(query)
    rows = result.all()
    return [
        {
            "merchant": r.merchant,
            "total_spent": round(float(r.total_spent), 2),
            "count": int(r.count)
        }
        for r in rows
    ]