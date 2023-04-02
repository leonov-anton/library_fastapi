from datetime import datetime, timedelta
from typing import Union, Optional

from fastapi import Depends, Cookie
from jose import JWTError, jwt

from src.config import JWT_SECRET, JWY_ALGORITHM
from src.exceptions import InvalidTokenException, AuthRequiredException, AuthAdminRequiredException
from .schema import JWTData


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
        raise InvalidTokenException
    return JWTData(**payload)


async def decode_jwt_data(token: Union[JWTData, None] = Depends(_decode_jwt_data)) -> JWTData:
    if not token:
        raise AuthRequiredException
    return token


async def decode_jwt_data_admin(token: JWTData = Depends(decode_jwt_data)) -> JWTData:
    if not token.is_admin:
        raise AuthAdminRequiredException
    return token
