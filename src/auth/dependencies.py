from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .jwt import decode_jwt_data, decode_jwt_data_admin
from .models import User
from .schema import JWTData
from .service import get_user
from ..db import get_async_session


async def get_current_user(
        jwt_data: JWTData = Depends(decode_jwt_data),
        session: AsyncSession = Depends(get_async_session)
) -> User:
    user = await get_user(jwt_data.id, session)
    return user


async def get_current_admin_user(
        jwt_data: JWTData = Depends(decode_jwt_data_admin),
        session: AsyncSession = Depends(get_async_session)
) -> User:
    user = await get_user(jwt_data.id, session)
    return user
