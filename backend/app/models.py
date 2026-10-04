from sqlalchemy import Column, Integer, String, Float, Date, DateTime, func
from backend.app.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    merchant = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False, index=True)
    transaction_date = Column(Date, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, nullable=False, index=True)
    category = Column(String(50), nullable=False)
    monthly_limit = Column(Float, nullable=False)
    month_year = Column(String(7), nullable=False)  # Format: "YYYY-MM"
    created_at = Column(DateTime, server_default=func.now())