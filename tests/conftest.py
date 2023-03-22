import asyncio
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, status, Response, Cookie
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.auth.jwt import create_access_token
from src.auth.schema import JWTData
from src.config import TEST_DATABASE_URL
from src.db import Base, get_async_session
from src.main import app

from src.auth.models import AuthRefreshToken

metadata = Base.metadata


test_engine = create_async_engine(TEST_DATABASE_URL)
async_session_maker = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
metadata.bind = test_engine

client = TestClient(app)


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session


@pytest_asyncio.fixture(autouse=True, scope='session')
async def run_db():
    """ Создание и удаление базы тестовой базы данных """
    async with test_engine.begin() as connection:
        await connection.run_sync(metadata.create_all)
    yield
    async with test_engine.begin() as connection:
        await connection.run_sync(metadata.drop_all)


@pytest_asyncio.fixture(scope='session')
async def get_test_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url='http://localhost:8000') as test_client:
        yield test_client


@pytest_asyncio.fixture(scope='session')
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def get_refresh_token_db() -> str:
    async with async_session_maker() as session:
        query = select(AuthRefreshToken).where(AuthRefreshToken.user_id == 1)
        db_refresh_token = await session.scalar(query)
        return db_refresh_token.refresh_token


@pytest_asyncio.fixture(scope='session')
async def access_login_user() -> str:
    return create_access_token(user=JWTData(sub=1))


@pytest_asyncio.fixture(scope='session')
async def access_login_another_user() -> str:
    return create_access_token(user=JWTData(sub=2))


@pytest_asyncio.fixture(scope='session')
async def access_login_admin() -> str:
    return create_access_token(user=JWTData(sub=3, is_admin=True))
