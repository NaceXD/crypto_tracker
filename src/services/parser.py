import httpx
import asyncio

from sqlalchemy import select
from src.database import async_session
from src.models import Currency


async def fetch_prices() -> dict:
    url = "https://api.bybit.com//v5/market/tickers?category=spot&symbol=BTCUSDT"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=10.0)
        if response.status_code != 200:
            raise Exception(f"Биржа вернула статус-код {response.status_code}")
        data = response.json()

        price_str = data["result"]["list"][0]["lastPrice"]
        return {"BTC": float(price_str)}

async def run_parser():
    while True:
        try:
            prices = await fetch_prices()
            btc_price = prices["BTC"]
            print(f"Парсер забрал цену BTC: {btc_price}$")

            async with async_session() as session:
                async with session.begin():
                    query = select(Currency).where(Currency.ticker == "BTC")
                    result = await session.execute(query)
                    currency = result.scalar_one_or_none()
                    if currency:
                        currency.current_price = btc_price
                    else:
                        new_currency = Currency(
                            ticker="BTC",
                            name="Биткоин",
                            current_price=btc_price,
                        )
                        session.add(new_currency)
                        print("Биткоин успешно добавлен в БД")

        except Exception as e:
            print(f"Ошибка в работе фонового парсера:{e}")

        await asyncio.sleep(60)