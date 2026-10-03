from backend.app.schemas import TransactionCreate
from fastapi import FastAPI

app = FastAPI(
    title="FinAI API",
    description="Backend service for FinAI Financial Assistant",
    version="0.1.0",
)

# A temporary in-memory list just to test receiving data
# (Tomorrow we replace this with real PostgreSQL!)
fake_transaction_db = []


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "FinAI API", "version": "0.1.0"}


@app.post("/transactions")
def create_transaction(transaction: TransactionCreate):
    # Convert validated Pydantic model to a standard dictionary
    saved_record = transaction.model_dump()

    # Assign a simple auto-incrementing ID
    saved_record["id"] = len(fake_transaction_db) + 1

    # Save to our temporary list
    fake_transaction_db.append(saved_record)

    return {
        "message": "Transaction created successfully",
        "data": saved_record,
    }


@app.get("/transactions")
def get_transactions():
    return {
        "count": len(fake_transaction_db),
        "transactions": fake_transaction_db,
    }