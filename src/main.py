import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.database import engine, Base
from src.models import User, Profile, Currency, Portfolio
from src.router.auth import router as auth_router
from src.router.portfolio import router as portfolio_router
from src.services.parser import run_parser


@asynccontextmanager
async def lifespan(_fastapi_app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    asyncio.create_task(run_parser())
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(portfolio_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}
