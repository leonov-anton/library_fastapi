from typing import List, Union, Any

from sqlalchemy import select, func, Result, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, with_expression

import src.books.schema as book_schema
from .models import Book, Rating, Comment, Author, Tag
from src.users.models import User

from pydantic import BaseModel
from src.db import Base


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
        .options(joinedload(Book.authors, ),
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

    book = await set_book_authors(book=book, authors_id=authors_id, session=session)

    session.add(book)
    await session.commit()
    await session.close()

    return book


async def set_book_authors(
        book: Union[Book, int],
        authors_id: List[int],
        session: AsyncSession
) -> Union[Book, None]:

    if isinstance(book, int):
        book = await get_book_data(book, session)
        if not book:
            return

    book.authors.clear()

    for a_id in authors_id:
        query = select(Author).where(Author.id == a_id)
        author = await session.scalar(query)
        if author:
            book.authors.append(author)

    return book


async def change_book_data(
        book_id: int,
        new_book_data: book_schema.BookPatchSchema,
        session: AsyncSession
) -> Book:
    book = await get_book_data(book_id, session)

    update_data = new_book_data.dict(exclude_unset=True, exclude_defaults=True)
    update_data.pop('id', None)

    authors_id = update_data.pop('authors_id', None)
    tags_id = update_data.pop('tags_id', None)

    if authors_id:
        book = await set_book_authors(book, authors_id, session)

    book = await change_instance(book_id, update_data, Book, session)

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
) -> Union[Author, None, str]:

    update_data = new_author_data.dict(exclude_unset=True, exclude_defaults=True)
    update_data.pop('id', None)

    if not update_data:
        return f'Данные не переданы.'

    query = update(Author).where(Author.id == author_id).values(**update_data).returning(Author)
    author = await session.scalar(query)

    if author is not None:
        await session.commit()
        return author


async def add_new_tag(
        content: book_schema.TagBase,
        session: AsyncSession,
) -> Union[Tag, None]:

    tag_data = content.dict(exclude_unset=True, exclude_defaults=True)
    tag_data.pop('id', None)

    if tag_data:
        tag = Tag(**tag_data)
        session.add(tag)
        await session.commit()

        return tag


async def get_tags_list(
        session: AsyncSession
):
    query = select(Tag)\
        .options(joinedload(Book.tags))\
        .group_by(Tag.id)\
        .order_by(Tag.id)

    res = await session.execute(query)
    return res.unique().scalars().all()


async def change_tag_data(
        tag_id: int,
        new_tag_data: book_schema.TagBase,
        session: AsyncSession
) -> Union[Tag, None, str]:
    update_data = new_tag_data.dict(exclude_unset=True, exclude_defaults=True)
    update_data.pop('id', None)

    if not update_data:
        return 'Данные не переданы.'

    query = update(Tag).where(Tag.id == tag_id).values(**update_data).returning(Tag)
    tag = await session.scalar(query)

    if tag is not None:
        await session.commit()
        return tag


async def change_instance(
        instance_id: int,
        new_instance_data: Union[BaseModel, dict],
        model: Base,
        session: AsyncSession
) -> Union[Base, None, str]:

    if not isinstance(new_instance_data, dict):
        update_data = new_instance_data.dict(exclude_unset=True, exclude_defaults=True)
        update_data.pop('id', None)
        if not update_data:
            return 'Данные не переданы.'
    else:
        update_data = new_instance_data

    query = update(model).where(model.id == instance_id).values(**update_data).returning(model)
    res = await session.scalar(query)

    if res is not None:
        return res


async def delete_instance(
        instance_id: int,
        model: Base,
        session: AsyncSession
) -> bool:
    query = select(model).where(model.id == instance_id)
    instance = await session.scalar(query)
    if not instance:
        return False
    await session.delete(instance)
    await session.commit()
    return True


async def _give_book_to_user(
        book_id: int,
        user_id: int,
        session: AsyncSession,
) -> Union[Book, None, str]:

    query_book = select(Book).where(Book.id == book_id).options(joinedload(Book.users))
    book = await session.scalar(query_book)
    if not book:
        return None

    query_user = select(User).where(User.id == user_id)
    user = await session.scalar(query_user)
    if book.available > 0 and user:
        book.available -= 1
        book.users.append(user)
        await session.commit()
        return book
    elif book.available == 0:
        return 'Книги нет в наличии.'


async def _get_book_from_user(
        book_id: int,
        user_id: int,
        session: AsyncSession,
) -> Union[Book, None]:

    query_book = select(Book).where(Book.id == book_id).options(joinedload(Book.users))
    book = await session.scalar(query_book)
    if not book:
        return None

    query_user = select(User).where(User.id == user_id)
    user = await session.scalar(query_user)
    if user:
        book.available += 1
        book.users.remove(user)
        await session.commit()
        return book