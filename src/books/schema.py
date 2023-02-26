from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, Field


class BookRating(BaseModel):
    id: int
    value: int = Field(ge=0, le=5)

    class Config:
        orm_mode = True


class BookTag(BaseModel):
    id: int
    content: str

    class Config:
        orm_mode = True


class BookComment(BaseModel):
    id: int
    content: str = Field(max_length=300)
    created: datetime

    class Config:
        orm_mode = True


class AuthorBase(BaseModel):
    id: Union[int, None] = 0
    name: str = 'Фамилия Имя'

    class Config:
        orm_mode = True


class BookBase(BaseModel):
    id: Union[int, None] = 0
    title: str = 'Название'
    year_published: Union[int, None] = None
    avg_rating: Union[float, None] = None

    class Config:
        orm_mode = True


class BookAuthorTag(BaseModel):
    authors: List[AuthorBase] = []
    tags: List[BookTag] = []


class BooksSchema(BookAuthorTag, BookBase):
    count_comments: int


class BooksAdminSchema(BooksSchema):
    quantity: int = 0
    available: int = 0


class BookSchema(BookAuthorTag, BookBase):
    comments: List[BookComment] = []


class BookAdminSchema(BookSchema):
    quantity: int = 0
    available: int = 0


class AuthorSchema(AuthorBase):
    books: List[BookBase] = []
