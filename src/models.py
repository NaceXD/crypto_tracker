from datetime import datetime
from sqlalchemy import String, DateTime, func, ForeignKey, Numeric, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from src.database import Base


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    profile: Mapped["Profile"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    portfolio_assets: Mapped[List["Portfolio"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )


class Profile(Base):
    __tablename__ = 'user_profiles'
    id: Mapped[int] = mapped_column(primary_key=True)
    bio: Mapped[Optional[str]] = mapped_column(String(255))
    balance: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0)
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    user: Mapped["User"] = relationship(back_populates="profile")


class Currency(Base):
    __tablename__ = 'currencies'
    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(String(10), nullable=False, index=True, unique=True)
    name: Mapped[str] = mapped_column(String(50))
    current_price: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    portfolio_holders: Mapped[List["Portfolio"]] = relationship(back_populates="currency")


class Portfolio(Base):
    __tablename__ = 'portfolios'
    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0)
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete="CASCADE"),
        nullable=False,
    )
    user: Mapped["User"] = relationship(back_populates="portfolio_assets")
    currency_id: Mapped[int] = mapped_column(
        ForeignKey('currencies.id', ondelete="CASCADE"),
        nullable=False,
    )
    currency: Mapped["Currency"] = relationship(back_populates="portfolio_holders")

    __table_args__ = (
        Index("user_currency_idx", "user_id", "currency_id"),
    )
