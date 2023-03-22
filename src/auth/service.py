from datetime import datetime, timedelta
from typing import Union, List

from fastapi import HTTPException, status
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from .models import User, AuthRefreshToken
from .schema import UserCreate, UserAuth
from .utils import hash_password, check_password, generate_alphanum_random_string
from src.books.models import Book, book_user


async def create_user(new_user_data: UserCreate, session: AsyncSession) -> User:
    if await check_email_and_username(new_user_data, session):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Пользотавель с таким данными уже зарегистрирован.'
        )

    user = User(
        email=new_user_data.email,
        username=new_user_data.username,
        hashed_password=hash_password(new_user_data.password)
    )

    session.add(user)
    await session.commit()
    return user


async def check_email_and_username(user_data: UserCreate, session: AsyncSession) -> bool:
    query = select(User).filter(or_(User.email == user_data.email, User.username == user_data.username))
    return await session.scalar(query)


async def get_user(user_id: int, session: AsyncSession) -> User:
    query = select(User).where(User.id == user_id)
    return await session.scalar(query)


async def user_books(user_id: int, session: AsyncSession) -> List[Book]:
    query = select(Book)\
        .filter(Book.users.any(id=user_id))

    print(query)

    res = await session.execute(query)

    return res.scalars().all()


async def authenticate_user(user_data: UserAuth, session: AsyncSession) -> User:
    query = select(User).where(User.email == user_data.email)
    user = await session.scalar(query)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Пользотавель с таким данными не зарегистрирован.'
        )

    if not check_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Пользотавель с таким данными не зарегистрирован.'
        )

    return user


async def create_refresh_token(user_id: int, session: AsyncSession) -> str:
    refresh_token = generate_alphanum_random_string()
    token = AuthRefreshToken(
        refresh_token=refresh_token,
        user_id=user_id,
        expires_at=datetime.utcnow() + timedelta(minutes=1440)
    )
    session.add(token)
    await session.commit()
    return refresh_token


async def get_refresh_token(
        user_refresh_token: str,
        session: AsyncSession
) -> Union[AuthRefreshToken, None]:
    query = select(AuthRefreshToken).where(AuthRefreshToken.refresh_token == user_refresh_token)
    return await session.scalar(query)


async def expire_refresh_token(user_refresh_token: str, session: AsyncSession) -> None:
    refresh_token = await get_refresh_token(user_refresh_token, session)
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Неверный токен.'
        )
    refresh_token.expires_at = datetime.utcnow() - timedelta(hours=24)
    await session.commit()


async def valid_refresh_token(user_refresh_token: str, session: AsyncSession) -> AuthRefreshToken:
    db_refresh_token = await get_refresh_token(user_refresh_token, session)
    if not db_refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Неверный токен.'
        )
    if db_refresh_token.expires_at <= datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Неверный токен.'
        )
    return db_refresh_token


async def get_user_from_refresh_token(user_refresh_token: str, session: AsyncSession) -> User:
    refresh_token = await valid_refresh_token(user_refresh_token, session)
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Неверный токен.'
        )
    return await get_user(refresh_token.user_id, session)
