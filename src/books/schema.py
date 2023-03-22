from datetime import datetime
from typing import List, Union, Optional

from pydantic import BaseModel, Field, validator, ValidationError

from src.auth.schema import UserResponse

# TODO:
#  упорядочить схемы, добавить валидацию


class RatingBase(BaseModel):
    id: Optional[int]
    value: int = Field(ge=0, le=5)

    class Config:
        orm_mode = True


class TagBase(BaseModel):
    id: Optional[int]
    content: str = Field(max_length=100)

    class Config:
        orm_mode = True


class CommentBase(BaseModel):
    id: Optional[int]
    content: str = Field(max_length=300)
    created: Optional[datetime]
    changed: Optional[Union[datetime, None]]

    class Config:
        orm_mode = True


class AuthorBase(BaseModel):
    id: Optional[int]
    name: str = 'Фамилия Имя'

    class Config:
        orm_mode = True


class BookBase(BaseModel):
    id: Optional[int]
    title: Optional[str]
    year_published: Optional[int]
    avg_rating: Optional[float]

    class Config:
        orm_mode = True


class AuthorSchema(AuthorBase):
    books: List[BookBase]


class BookAuthor(BaseModel):
    authors: List[AuthorBase] = []


class BooksSchema(BookBase):
    count_comments: int = 0
    authors: List[AuthorBase] = []
    tags: List[TagBase] = []


class BooksAdminSchema(BooksSchema):
    users: Optional[List[UserResponse]]
    quantity: Optional[int]
    available: Optional[int]


class BookSchema(BookBase):
    description: Optional[str] = Field(max_length=250)
    comments: Optional[List[CommentBase]]
    authors: Optional[List[AuthorBase]]
    tags: Optional[List[TagBase]]


class BookAdminSchema(BookSchema):
    users: Optional[List[UserResponse]]
    quantity: Optional[int]
    available: Optional[int]


class BookUpdateSchema(BaseModel):
    title: Optional[str]
    year_published: Optional[int]
    description: Optional[str] = Field(max_length=300)
    authors_id: Optional[List[int]]
    tags_id: Optional[List[int]]
    quantity: Optional[int] = Field(ge=0)

    @validator('year_published')
    def year_early_current(cls, v):
        if v and v > datetime.utcnow().year:
            raise ValueError('Этот год еще не настал.')
        return v


class AuthorSchema(AuthorBase):
    books: List[BookBase] = []


class TagSchema(TagBase):
    books: Optional[List[BookBase]]
