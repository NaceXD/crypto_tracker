from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import List, Optional


class CurrencyResponse(BaseModel):
    id: int
    ticker: str
    name: str
    current_price: float
    updated_at: datetime

    model_config = {"from_attributes": True}


class PortfolioResponse(BaseModel):
    id: int
    amount: float
    currency: CurrencyResponse

    model_config = {"from_attributes": True}


class ProfileResponse(BaseModel):
    id: int
    bio: Optional[str] = None
    balance: float
    model_config = {"from_attributes": True}


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserResponse(UserBase):
    id: int
    created_at: datetime
    profile: Optional[ProfileResponse] = None
    portfolio_assets: List[PortfolioResponse] = []
    model_config = {"from_attributes": True}

class AssetDepositSchema(BaseModel):
    ticker: str = Field(..., min_length=2, max_length=10)
    amount: float = Field(..., gt=0)

class UserPortfolioReportSchema(BaseModel):
    user_id: int
    assets: List[PortfolioResponse]
    total_crypto_balance_usd: float
    calculated_at: datetime

    model_config = {"from_attributes": True}