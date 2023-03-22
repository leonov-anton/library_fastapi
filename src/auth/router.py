from typing import Optional, Dict

from fastapi import APIRouter, Depends, status, Response, Cookie
from sqlalchemy.ext.asyncio import AsyncSession

from .jwt import decode_jwt_data, create_access_token
from .schema import UserCreate, UserResponse, UserAuth, JWTData, TokenResponse, UserBooks
from .service import (
    create_user,
    get_user,
    authenticate_user,
    create_refresh_token,
    expire_refresh_token,
    valid_refresh_token,
    get_user_from_refresh_token,
    user_books,
)
from ..db import get_async_session

router = APIRouter(
    prefix='/auth',
    tags=['Auth']
)


@router.post('/register',
             status_code=status.HTTP_201_CREATED,
             response_model=UserResponse)
async def user_registration(
        new_user_data: UserCreate,
        session: AsyncSession = Depends(get_async_session)
):
    result = await create_user(new_user_data, session)
    return result


@router.get('/user',
            status_code=status.HTTP_200_OK,
            response_model=UserResponse)
async def get_user_data(
        jwt_data: JWTData = Depends(decode_jwt_data),
        session: AsyncSession = Depends(get_async_session)
):
    user = await get_user(jwt_data.id, session)
    return user


@router.post('/user/token',
             status_code=status.HTTP_200_OK,
             response_model=TokenResponse)
async def user_auth(
        user_data: UserAuth,
        response: Response,
        session: AsyncSession = Depends(get_async_session)
):
    user = await authenticate_user(user_data, session)

    access_token = create_access_token(user)
    refresh_token = await create_refresh_token(user.id, session)

    response.set_cookie(
        key='access_token',
        value=access_token,
        httponly=True,
        secure=True,
        max_age=3600
    )

    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,
        secure=True,
        max_age=86400
    )
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.put('/user/token',
            status_code=status.HTTP_200_OK,
            response_model=TokenResponse)
async def refresh_tokens(
        response: Response,
        session: AsyncSession = Depends(get_async_session),
        user_refresh_token: Optional[str] = Cookie(default=None, alias='refresh_token')
):
    refresh_token = await valid_refresh_token(user_refresh_token, session)

    user = await get_user_from_refresh_token(user_refresh_token, session)
    await expire_refresh_token(user_refresh_token, session)

    new_access_token = create_access_token(user)
    new_refresh_token = await create_refresh_token(refresh_token.user_id, session)

    response.set_cookie(
        key='access_token',
        value=new_access_token,
        httponly=True,
        secure=True,
        max_age=3600
    )

    response.set_cookie(
        key='refresh_token',
        value=new_refresh_token,
        httponly=True,
        secure=True,
        max_age=86400
    )

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token
    )


@router.delete('/user/token', status_code=status.HTTP_200_OK)
async def user_logout(
        response: Response,
        session: AsyncSession = Depends(get_async_session),
        user_refresh_token: Optional[str] = Cookie(default=None, alias='refresh_token')
) -> Dict[str, str]:
    await expire_refresh_token(user_refresh_token, session)

    response.delete_cookie(key='access_token')
    response.delete_cookie(key='refresh_token')

    return {'Message': 'Выход выполнен.'}


@router.get(
    '/user/books',
    status_code=status.HTTP_200_OK)
async def get_user_books(
        jwt_data: JWTData = Depends(decode_jwt_data),
        session: AsyncSession = Depends(get_async_session)
):
    books = await user_books(jwt_data.id, session)
    return books
