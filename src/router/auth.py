import hashlib
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.models import User, Profile
from src.schemas import UserCreate, UserResponse, UserLogin

router = APIRouter(prefix="/auth", tags=["Auth"])


def hash_password(password: str) -> str:
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    return password_hash


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, session: AsyncSession = Depends(get_db)):
    query = select(User).where(User.email == user_data.email)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь с таким email уже существует")

    hashed_password = hash_password(user_data.password)

    async with session.begin():
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password
        )
        session.add(new_user)
        await session.flush()
        new_profile = Profile(user_id=new_user.id)
        session.add(new_profile)
    await session.refresh(new_user)

    return new_user

@router.post("/login", response_model=UserResponse)
async def login_user(user_data: UserLogin, session: AsyncSession = Depends(get_db)):
    query = select(User).where(User.email == user_data.email)
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    password = hash_password(user_data.password)
    if not user or password != user.hashed_password:
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    return user