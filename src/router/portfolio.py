import asyncio
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from datetime import datetime, timezone
from decimal import Decimal
from concurrent.futures import ProcessPoolExecutor
from src.database import get_db
from src.models import Portfolio, Currency
from src.schemas import AssetDepositSchema, PortfolioResponse, UserPortfolioReportSchema
from src.services.analytics import calculate_single_portfolio_metrics

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])


@router.post("/deposit", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
async def deposit_asset(
        user_id: int,
        asset_data: AssetDepositSchema,
        session: AsyncSession = Depends(get_db)
):
    try:
        async with session.begin():

            query = select(Currency).where(Currency.ticker == asset_data.ticker.upper())
            result = await session.execute(query)
            currency = result.scalar_one_or_none()

            if currency is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Валюта не поддерживается парсером"
                )

            query = select(Portfolio).where(
                Portfolio.user_id == user_id,
                Portfolio.currency_id == currency.id
            )
            result = await session.execute(query)
            portfolio = result.scalar_one_or_none()

            if portfolio:
                portfolio.amount += asset_data.amount
                target_id = portfolio.id
            else:
                new_portfolio = Portfolio(
                    amount=asset_data.amount,
                    user_id=user_id,
                    currency_id=currency.id
                )
                session.add(new_portfolio)
                await session.flush()
                target_id = new_portfolio.id
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при сохранении в БД: {e}"
        )

    stmt = (
        select(Portfolio)
        .where(Portfolio.id == target_id)
        .options(joinedload(Portfolio.currency))
    )
    refresh_result = await session.execute(stmt)
    return refresh_result.scalar_one()


@router.get("/me", response_model=UserPortfolioReportSchema)
async def get_user_portfolio(user_id: int, session: AsyncSession = Depends(get_db)):
    query = select(Portfolio).where(Portfolio.user_id == user_id).options(joinedload(Portfolio.currency))
    result = await session.execute(query)
    assets = result.scalars().all()

    total_balance = Decimal("0.0")

    for asset in assets:
        total_balance += asset.amount * asset.currency.current_price

    return {
        "user_id": user_id,
        "assets": assets,
        "total_crypto_balance_usd": total_balance,
        "calculated_at": datetime.now(timezone.utc),
    }


@router.get("/analytics/all")
async def get_all_portfolios_analytics(session: AsyncSession = Depends(get_db)):
    query = select(Portfolio).options(joinedload(Portfolio.currency))
    result = await session.execute(query)
    all_asset = result.scalars().all()

    raw_data_map = {}
    for asset in all_asset:
        uid = asset.user_id
        if uid not in raw_data_map:
            raw_data_map[uid] = {"user_id": uid, "total_value": 0.0, "assets": []}
        asset_value = float(asset.amount * asset.currency.current_price)
        raw_data_map[uid]["total_value"] += asset_value
        raw_data_map[uid]["assets"].append({
            "ticker": asset.currency.ticker,
            "amount": float(asset.amount),
            "price": float(asset.currency.current_price)
        })
    portfolios_list = list(raw_data_map.values())

    if not portfolios_list:
        return {"message": "Нет данных для расчета"}

    loop = asyncio.get_running_loop()
    with ProcessPoolExecutor(max_workers=2) as executor:
        def run_parallel_mapping():
            return list(executor.map(calculate_single_portfolio_metrics, portfolios_list))

        analytics_results = await loop.run_in_executor(
            None,
            run_parallel_mapping,
        )
    return {"status": "success", "data": analytics_results}
