from datetime import datetime
from typing import List, Union, Optional

from pydantic import BaseModel, Field, validator, ValidationError

from src.users.schema import UserRead

# TODO:
#  упорядочить схемы, добавить валидацию


class RatingBase(BaseModel):
    id: Optional[int]
    value: int = Field(ge=0, le=5)

    class Config:
        orm_mode = True


class TagBase(BaseModel):
    id: Union[int, None] = None
    content: str = ''

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
    id: int
    title: str = 'Название'
    year_published: Optional[int]
    avg_rating: Optional[float]

    class Config:
        orm_mode = True


class AuthorSchema(AuthorBase):
    books: List[BookBase]


class BookAuthor(BaseModel):
    authors: List[AuthorBase] = []


class BookTag(BaseModel):
    tags: List[TagBase] = []


class BooksSchema(BookBase):
    count_comments: int = 0
    authors: List[AuthorBase] = []
    tags: List[TagBase] = []


class BooksAdminSchema(BooksSchema):
    users: List[UserRead] = []
    quantity: int = 0
    available: int = 0


class BookSchema(BookBase):
    description: Optional[str] = Field(max_length=250)
    comments: Optional[List[CommentBase]]
    authors: Optional[List[AuthorBase]]
    tags: Optional[List[TagBase]]


class BookAdminSchema(BookSchema):
    users: Optional[List[UserRead]]
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
    books: List[BookBase] = []
