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


@pytest.mark.asyncio
async def test_analytics_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Seed 2 transactions
        await client.post("/transactions", json={
            "account_id": 1,
            "amount": 2000.0,
            "merchant": "Amazon",
            "category": "Shopping",
            "transaction_date": "2026-10-01"
        })
        await client.post("/transactions", json={
            "account_id": 1,
            "amount": 1000.0,
            "merchant": "Swiggy",
            "category": "Food",
            "transaction_date": "2026-10-02"
        })

        # Test summary
        res_summary = await client.get("/analytics/summary")
        assert res_summary.status_code == 200
        summary_data = res_summary.json()
        assert summary_data["total_spent"] == 3000.0
        assert summary_data["transaction_count"] == 2
        assert summary_data["average_transaction"] == 1500.0

        # Test category breakdown
        res_cat = await client.get("/analytics/categories")
        assert res_cat.status_code == 200
        cats = res_cat.json()
        assert len(cats) == 2
        # Amazon Shopping (2000 / 3000 = 66.67%)
        assert cats[0]["category"] == "Shopping"
        assert cats[0]["percentage"] == 66.67

        # Test top merchants
        res_merchants = await client.get("/analytics/merchants")
        assert res_merchants.status_code == 200
        merchants = res_merchants.json()
        assert merchants[0]["merchant"] == "Amazon"
        assert merchants[0]["total_spent"] == 2000.0