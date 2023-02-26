from typing import List, Union, Any

from sqlalchemy import select, func, Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, with_expression

import src.books.schema as book_schema
from .models import Book, Rating, Comment, Author


async def get_books_list(session: AsyncSession) -> List[Book]:

    books = select(Book) \
        .outerjoin(Rating) \
        .outerjoin(Comment) \
        .options(joinedload(Book.authors),
                 joinedload(Book.tags),
                 with_expression(Book.avg_rating, func.avg(Rating.value).label('avg_rating')),
                 with_expression(Book.count_comments, func.count(Comment.id).label('count_comments'))) \
        .group_by(Book.id) \
        .order_by(Book.id)

    res = await session.execute(books)
    return res.unique().scalars().all()


async def get_book_data(book_id: int, session: AsyncSession) -> Book:
    query = select(Book)\
        .where(Book.id == book_id) \
        .outerjoin(Rating) \
        .options(joinedload(Book.authors),
                 joinedload(Book.tags),
                 joinedload(Book.comments).load_only(Comment.id, Comment.content, Comment.created),
                 with_expression(Book.avg_rating, func.avg(Rating.value).label('avg_rating')))\
        .group_by(Book.id)

    res = await session.execute(query)
    return res.scalar()


async def add_new_book(
        book_data: book_schema.BookAdminSchema,
        authors_id: List[int],
        session: AsyncSession
) -> Book:

    book_data_dict = book_data.dict()
    book_data_dict.pop('id')
    book_data_dict['available'] = book_data_dict['quantity']

    book = Book(**book_data_dict)

    await set_book_authors(book=book, authors_id=authors_id, session=session)

    session.add(book)
    await session.commit()
    await session.close()

    return book


async def set_book_authors(
        book: Union[Book, int],
        authors_id: List[int],
        session: AsyncSession
) -> None:

    if isinstance(book, int):
        query = select(Book).where(Book.id == book)
        book = await session.scalar(query)
        if not book:
            return

    for a_id in authors_id:
        query = select(Author).where(Author.id == a_id)
        author = await session.scalar(query)
        if author:
            book.authors.append(author)


async def change_book_data(
        book_id: int,
        new_book_data: book_schema.BookAdminSchema,
        session: AsyncSession
) -> Book:
    book = await get_book_data(book_id, session)

    update_data = new_book_data.dict(exclude_unset=True, exclude_defaults=True)
    update_data.pop('id')

    for key, value in update_data.items():
        setattr(book, key, value)
    await session.commit()

    return book


async def create_author(author_name: str, session: AsyncSession) -> Author:
    author = Author(name=author_name)
    session.add(author)

    await session.commit()
    await session.close()

    return author


async def get_author_data(author_id: int, session: AsyncSession) -> Union[Author, None]:
    query = select(Author).where(Author.id == author_id)
    author = await session.scalar(query)
    if author:
        return author


async def change_author_data(
        author_id: int,
        new_author_data: book_schema.AuthorBase,
        session: AsyncSession
) -> Author:
    author = await get_author_data(author_id, session)

    update_data = new_author_data.dict(exclude_unset=True, exclude_defaults=True)
    update_data.pop('id')

    for key, value in update_data.items():
        setattr(author, key, value)
    await session.commit()

    return author