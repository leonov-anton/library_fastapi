from datetime import datetime
from typing import List, Union

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import select, func, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, with_expression

import src.books.schema as book_schema
from src.db import Base
from src.auth.models import User
from .models import Book, Rating, Comment, Author, Tag, book_user


async def get_books_list(filter_str: str, session: AsyncSession) -> List[Book]:
    search_str = '%' + filter_str + '%'
    query = select(Book) \
        .filter(Book.title.ilike(search_str) | Book.description.ilike(search_str)) \
        .outerjoin(Rating) \
        .outerjoin(Comment) \
        .options(joinedload(Book.authors),
                 joinedload(Book.tags),
                 joinedload(Book.users),
                 with_expression(Book.avg_rating, func.avg(Rating.value).label('avg_rating')),
                 with_expression(Book.count_comments, func.count(Comment.id).label('count_comments'))) \
        .group_by(Book.id) \
        .order_by(Book.id)

    res = await session.execute(query)
    return res.unique().scalars().all()


async def get_book_data(book_id: int, session: AsyncSession) -> Union[Book, None]:
    query = select(Book)\
        .where(Book.id == book_id) \
        .outerjoin(Rating) \
        .options(joinedload(Book.authors),
                 joinedload(Book.tags),
                 joinedload(Book.users),
                 joinedload(Book.comments).load_only(Comment.id, Comment.content, Comment.created, Comment.changed),
                 with_expression(Book.avg_rating, func.avg(Rating.value).label('avg_rating')))\
        .group_by(Book.id)

    res = await session.execute(query)
    if res is not None:
        return res.scalar()


async def get_authors_list(filter_str: str, session: AsyncSession) -> List[Author]:
    search_str = '%' + filter_str + '%'
    query = select(Author)\
        .filter(Author.name.ilike(search_str)) \
        .options(joinedload(Author.books))\
        .order_by(Author.name)\
        .group_by(Author.id)

    res = await session.execute(query)
    return res.unique().scalars().all()


async def get_author_book_list(author_id: int, session: AsyncSession) -> List[Book]:
    query = select(Book) \
        .filter(Book.authors.any(id=author_id)) \
        .outerjoin(Rating) \
        .outerjoin(Comment) \
        .options(joinedload(Book.authors),
                 joinedload(Book.tags),
                 joinedload(Book.users),
                 with_expression(Book.avg_rating, func.avg(Rating.value).label('avg_rating')),
                 with_expression(Book.count_comments, func.count(Comment.id).label('count_comments'))) \
        .group_by(Book.id) \
        .order_by(Book.id)

    res = await session.execute(query)
    return res.unique().scalars().all()


async def add_new_book(
        book_data: book_schema.BookUpdateSchema,
        session: AsyncSession
) -> Book:

    book_data_dict = book_data.dict(exclude_unset=True)
    book_data_dict['available'] = book_data_dict['quantity']
    authors_id = book_data_dict.pop('authors_id', None)
    tags_id = book_data_dict.pop('tags_id', None)

    book = Book(**book_data_dict)

    if authors_id:
        book = await set_book_authors(book, authors_id, session)
    if tags_id:
        book = await set_book_tags(book, tags_id, session)
    session.add(book)
    await session.commit()

    return await get_book_data(book.id, session)


async def update_book_data(
        book_id: int,
        new_book_data: book_schema.BookUpdateSchema,
        session: AsyncSession
) -> Union[Book, None]:

    book = await get_book_data(book_id, session)

    if not book:
        return None

    update_data = new_book_data.dict(exclude_unset=True)
    authors_id = update_data.pop('authors_id', None)
    tags_id = update_data.pop('tags_id', None)

    if 'quantity' in update_data:
        if update_data['quantity'] == 0:
            update_data['available'] = 0
        else:
            update_data['available'] = book.available + (update_data['quantity'] - book.quantity)

    for key, value in update_data.items():
        setattr(book, key, value)

    if authors_id:
        book = await set_book_authors(book, authors_id, session)
    if tags_id:
        book = await set_book_tags(book, tags_id, session)

    await session.commit()
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


async def set_book_tags(
        book: Union[Book, int],
        tags_id: List[int],
        session: AsyncSession

) -> Union[Book, None]:

    if isinstance(book, int):
        book = await get_book_data(book, session)
        if not book:
            return

    book.tags.clear()

    for t_id in tags_id:
        query = select(Tag).where(Tag.id == t_id)
        tag = await session.scalar(query)
        if tag:
            book.tags.append(tag)

    return book


async def create_author(author_name: str, session: AsyncSession) -> Author:
    author = Author(name=author_name)
    session.add(author)

    await session.commit()

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
    query = select(Tag).options(joinedload(Tag.books)).group_by(Tag.id).order_by(Tag.id)
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
        update_data = new_instance_data.dict(exclude_unset=True)
        update_data.pop('id', None)
        if not update_data:
            return 'Данные не переданы.'
    else:
        update_data = new_instance_data

    query = update(model).where(model.id == instance_id).values(**update_data).returning(model)
    res = await session.execute(query)

    if res is not None:
        return res.scalar()


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
) -> Book:

    query_book = select(Book).where(Book.id == book_id).options(joinedload(Book.users))
    book = await session.scalar(query_book)
    if not book:
        raise HTTPException(
            status_code=404,
            detail='Книга не найдена.'
        )

    query_user = select(User).where(User.id == user_id)
    user = await session.scalar(query_user)
    if not user:
        raise HTTPException(
            status_code=404,
            detail='Пользователь не найден.'
        )

    if book.available > 0:
        book.available -= 1
        book.users.append(user)
        await session.commit()
        return book
    elif book.available == 0:
        raise HTTPException(
            status_code=404,
            detail='Книги нет в наличии.'
        )


async def _get_book_from_user(
        book_id: int,
        user_id: int,
        session: AsyncSession,
) -> Book:

    statement = update(book_user)\
        .values(returned_at=datetime.utcnow()) \
        .where(and_(book_user.c.book_id == book_id,
                    book_user.c.user_id == user_id,
                    book_user.c.returned_at == None))\
        .returning(book_user)

    book = await session.scalar(statement)

    print(book)

    if not book:
        raise HTTPException(
            status_code=404,
            detail='Пользователь не брал эту кгину.'
        )

    query_book = select(Book).where(Book.id == book_id).options(joinedload(Book.users))
    book = await session.scalar(query_book)
    if not book:
        raise HTTPException(
            status_code=404,
            detail='Книга не найдена.'
        )

    book.available += 1
    await session.commit()
    return book


async def _update_comment(
        comment_id,
        new_comment: book_schema.CommentBase,
        session: AsyncSession,
        user: User
) -> Union[Comment, None, str]:

    query = select(Comment).where(Comment.id == comment_id)
    comment = await session.scalar(query)
    if not comment:
        return None
    if comment.user_id != user.id:
        return 'Комметрий оставлен другим пользователем.'

    update_data = new_comment.dict(exclude_unset=True)
    update_data.pop(id, None)
    if 'content' not in update_data:
        return 'Данные не переданы.'

    comment.content = update_data['content']
    comment.changed = datetime.utcnow()

    return comment


async def _set_rating(
        book_id: int,
        rating: book_schema.RatingBase,
        session: AsyncSession,
        user: User
) -> Union[Rating, str]:

    update_data = rating.dict(exclude_unset=True)
    update_data.pop('id', None)

    statement = update(Rating)\
        .where(and_(Rating.user == user, Rating.book_id == book_id))\
        .values(**update_data)\
        .returning(Rating)

    res = await session.scalar(statement)
    if not res:
        res = Rating(value=rating.value, book_id=book_id, user_id=user.id)
        session.add(res)

    await session.commit()
    return res
