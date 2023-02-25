from datetime import datetime
from typing import List, Optional

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
    id: int
    name: str

    class Config:
        orm_mode = True


class BookBase(BaseModel):
    id: int
    title: str
    year_published: Optional[int]
    avg_rating: Optional[float]

    authors: List[AuthorBase]
    tags: List[BookTag]

    class Config:
        orm_mode = True


class BooksSchema(BookBase):
    count_comments: int


class BookSchema(BookBase):
    comments: List[BookComment] = []


class AuthorSchema(AuthorBase):
    books: List[BookBase]
