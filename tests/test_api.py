import pytest
from httpx import ASGITransport, AsyncClient
from backend.app.main import app
from backend.app.database import engine, Base


@pytest.fixture(autouse=True)
async def setup_test_db():
    """Automatically create all tables in SQLite before tests, and drop them after."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_health_check():
    """Verify that the API is alive and reachable (HTTP 200)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "FinAI API"


@pytest.mark.asyncio
async def test_get_transactions():
    """Verify that transactions list endpoint responds with 200 and expected schema."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/transactions")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "transactions" in data
        assert isinstance(data["transactions"], list)


@pytest.mark.asyncio
async def test_invalid_transaction_negative_amount():
    """Verify that Pydantic rejects negative transactions (HTTP 422)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "account_id": 1,
            "amount": -500.00,
            "merchant": "Test Store",
            "category": "Shopping",
            "transaction_date": "2026-10-04"
        }
        response = await client.post("/transactions", json=payload)
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_invalid_transaction_missing_fields():
    """Verify that requests missing required fields fail immediately."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"account_id": 1}
        response = await client.post("/transactions", json=payload)
        assert response.status_code == 422