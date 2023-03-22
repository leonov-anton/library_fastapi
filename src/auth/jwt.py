from datetime import datetime, timedelta
from typing import Union, Optional

from jose import JWTError, jwt

from fastapi import Depends, HTTPException, status, Cookie

from .schema import JWTData
from src.config import JWT_SECRET, JWY_ALGORITHM


def create_access_token(user: JWTData, exp_delta: timedelta = timedelta(minutes=60)) -> str:
    data = {
        'sub': str(user.id),
        'exp': datetime.utcnow() + exp_delta,
        'is_admin': user.is_admin
    }

    return jwt.encode(data, key=JWT_SECRET, algorithm=JWY_ALGORITHM)


async def _decode_jwt_data(
        access_token: Optional[str] = Cookie(default=None, alias='access_token')
) -> Union[JWTData, None]:

    if not access_token:
        return None
    try:
        payload = jwt.decode(token=access_token, key=JWT_SECRET, algorithms=[JWY_ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Неверный токен.',
        )
    return JWTData(**payload)


async def decode_jwt_data(token: Union[JWTData, None] = Depends(_decode_jwt_data)) -> JWTData:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Необходима аутентификация.'
        )
    return token


async def decode_jwt_data_admin(token: JWTData = Depends(decode_jwt_data)) -> JWTData:
    if not token.is_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Необходимы права администратора.'
        )
    return token
