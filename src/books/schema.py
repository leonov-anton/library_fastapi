from datetime import datetime
from typing import List, Union, Optional

from pydantic import BaseModel, Field


# TODO:
#  упорядочить схемы, добавить валидацию

class BookRating(BaseModel):
    id: Union[int, None] = None
    value: int = Field(ge=0, le=5)

    class Config:
        orm_mode = True


class TagBase(BaseModel):
    id: Union[int, None] = None
    content: str = ''

    class Config:
        orm_mode = True


class BookComment(BaseModel):
    id: Union[int, None] = None
    content: str = Field(max_length=300)
    created: datetime

    class Config:
        orm_mode = True


class AuthorBase(BaseModel):
    id: Union[int, None] = None
    name: str = 'Фамилия Имя'

    class Config:
        orm_mode = True


class BookBase(BaseModel):
    id: Union[int, None] = None
    title: str = 'Название'
    year_published: Union[int, None] = None
    avg_rating: Union[float, None] = None

    class Config:
        orm_mode = True


class BookAuthor(BaseModel):
    authors: List[AuthorBase] = []


class BookTag(BaseModel):
    tags: List[TagBase] = []


class BooksSchema(BookBase):
    count_comments: int
    authors: List[AuthorBase] = []
    tags: List[TagBase] = []


class BooksAdminSchema(BooksSchema):
    quantity: int = 0
    available: int = 0


class BookSchema(BookBase):
    comments: List[BookComment] = []
    authors: List[AuthorBase] = []
    tags: List[TagBase] = []


class BookAdminSchema(BookSchema):
    quantity: int = 0
    available: int = 0


class BookPatchSchema(BaseModel):
    title: str = 'Название'
    year_published: int
    description: str = Field(max_length=300)
    quantity: int
    available: int


class AuthorSchema(AuthorBase):
    books: List[BookBase] = []


class TagSchema(TagBase):
    books: List[BookBase] = []
