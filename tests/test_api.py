import pytest
from httpx import AsyncClient
from src.models import Currency


@pytest.mark.asyncio(loop_scope="session")
async def test_register_user_success(client: AsyncClient):
    user_data = {
        "username": "test_user_pytest",
        "email": "pytest_test@example.com",
        "password": "secret_password_123"
    }
    response = await client.post("/auth/register", json=user_data)
    assert response.status_code == 201

    data = response.json()
    assert "id" in data
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]


@pytest.mark.asyncio(loop_scope="session")
async def test_login_user_success(client: AsyncClient):
    login_data = {
        "email": "pytest_test@example.com",
        "password": "secret_password_123"
    }

    response = await client.post("/auth/login", json=login_data)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == login_data["email"]
    assert "id" in data
    assert "password" not in data


@pytest.mark.asyncio(loop_scope="session")
async def test_deposit_asset_success(client: AsyncClient, db_session):
    test_currency = Currency(
        ticker="BTC",
        name="Биткоин",
        current_price=84000.00
    )
    db_session.add(test_currency)
    await db_session.commit()

    deposit_data = {
        "ticker": "BTC",
        "amount": "0.5"
    }

    response = await client.post("/portfolio/deposit?user_id=1", json=deposit_data)

    assert response.status_code == 201
    data = response.json()

    assert float(data["amount"]) == 0.5
    assert data["currency"]["ticker"] == "BTC"
    assert float(data["currency"]["current_price"]) == 84000.00


@pytest.mark.asyncio(loop_scope="session")
async def test_get_all_portfolios_analytics_success(client: AsyncClient):
    response = await client.get("/portfolio/analytics/all")

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "success"
    assert "data" in data
    assert len(data["data"]) > 0

    user_analytics = data["data"][0]
    assert user_analytics["user_id"] == 1
    assert "total_value_usd" in user_analytics
    assert "risk_score" in user_analytics

    assert user_analytics["diversification"]["BTC"] == 100.0
