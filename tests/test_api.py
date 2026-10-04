import pytest
from httpx import ASGITransport, AsyncClient
from backend.app.main import app
from backend.app.database import engine, Base

@pytest.fixture(autouse=True)
async def setup_test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_health_check():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "FinAI API"

@pytest.mark.asyncio
async def test_create_and_get_transaction():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "account_id": 1,
            "amount": 1250.50,
            "merchant": "Swiggy",
            "category": "Food",
            "transaction_date": "2026-10-04"
        }
        res_post = await client.post("/transactions", json=payload)
        assert res_post.status_code == 201
        created = res_post.json()
        assert created["merchant"] == "Swiggy"

        res_get = await client.get("/transactions")
        assert res_get.status_code == 200
        data = res_get.json()
        assert data["count"] >= 1

@pytest.mark.asyncio
async def test_invalid_transaction_negative_amount():
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
async def test_create_and_get_budget():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "account_id": 1,
            "category": "Food",
            "monthly_limit": 15000.0,
            "month_year": "2026-10"
        }
        res_post = await client.post("/budgets", json=payload)
        assert res_post.status_code == 201
        created = res_post.json()
        assert created["category"] == "Food"
        assert created["monthly_limit"] == 15000.0

        res_get = await client.get("/budgets")
        assert res_get.status_code == 200
        budgets = res_get.json()
        assert len(budgets) == 1
        assert budgets[0]["month_year"] == "2026-10"

@pytest.mark.asyncio
async def test_invalid_budget_month_format():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Invalid month format (not YYYY-MM)
        payload = {
            "account_id": 1,
            "category": "Rent",
            "monthly_limit": 20000.0,
            "month_year": "10-2026"
        }
        response = await client.post("/budgets", json=payload)
        assert response.status_code == 422