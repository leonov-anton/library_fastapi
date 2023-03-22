import re
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, validator
# from src.books.schema import BooksSchema


class JWTData(BaseModel):
    id: int = Field(alias='sub')
    is_admin: bool = False

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str = Field(min_length=6, max_length=26)

    @validator('password')
    def validate_passvord(cls, password: str) -> str:
        if not re.match(r'^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z!@#$%^&*]{6,26}$', password):
            raise ValueError(
                'Пароль должен содержать хоты бы одну '
                'строчку букву и заглавную букву (только латинские), '
                'цифру,'
                'символ из набора - !@#$%^&*')
        return password

    class Config:
        orm_mode = True


class UserAuth(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=26)

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    email: EmailStr
    username: str
    is_admin: bool

    class Config:
        orm_mode = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str

    class Config:
        orm_mode = True


class UserBooks:
    field: str
    # give_at: datetime
    # returned_at: datetime

