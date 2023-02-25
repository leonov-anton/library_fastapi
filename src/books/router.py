from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, with_expression

import src.books.schema as book_schema
from src.db import get_async_session
from src.users.models import User
from src.users.auth_config import fastapi_users
from .models import Book, Rating, Comment

router = APIRouter(
    prefix='/book',
    tags=['Book']
)


@router.get('/', response_model=List[book_schema.BooksSchema])
async def get_books(limmit: int = 20,
                    offset: int = 0,
                    session: AsyncSession = Depends(get_async_session)
                    ) -> List[book_schema.BooksSchema]:
    """
    Эндпоинт всех книг. Пагинация, по умолчанию 10.
    :param limmit: Кол-во выводимых книг.
    :param offset: Номер набора по limmit.
    :param session: сессия БД
    :return: Книга: id, название, авторы, год, средний рейтинг, кол-во коментариев, теги
    """

    books = select(Book)\
        .outerjoin(Rating)\
        .outerjoin(Comment)\
        .options(joinedload(Book.authors),
                 joinedload(Book.tags),
                 with_expression(Book.avg_rating, func.avg(Rating.value).label('avg_rating')),
                 with_expression(Book.count_comments, func.count(Comment.id).label('count_comments')))\
        .group_by(Book.id)\
        .order_by(Book.id)

    res = await session.execute(books)

    return res.unique().scalars().all()[offset:][:limmit]


@router.get('/{book_id}')
async def get_book(book_id: int,
                   session: AsyncSession = Depends(get_async_session)
                   ):
    """
    Энедпоин одной книги.
    :param book_id: id по каталогу
    :param session: сессия БД
    :return: Книга: id, название, авторы, год, средний рейтинг, комментарии к книге, теги
    """
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


@router.post('/{book_id}/rating')
async def set_rating(book_id: int,
                     rating: book_schema.BookRating,
                     session: AsyncSession = Depends(get_async_session),
                     user: User = Depends(fastapi_users.current_user())
                     ):
    """
    Энепоин руйтинга книги от пользователя.
    :param user: Пользователь.
    :param book_id: id книги по каталогу.
    :param rating: Рейтинг от пользователя.
    :param session: Сессия БД.
    :return: Сообщение - рейтинг учтен.
    """
    rating = Rating(value=rating.value, book_id=book_id, user_id=user.id)
    session.add(rating)

    await session.commit()
    await session.close()

    return {f'{user.username}, ваша оценка учтена!'}


@router.post('/{book_id}/comment')
async def set_comment(book_id: int,
                      comment: book_schema.BookComment,
                      session: AsyncSession = Depends(get_async_session),
                      user: User = Depends(fastapi_users.current_user())
                      ):
    """
    Эндпоин комментария от пользователя.
    :param user: Пользователь.
    :param book_id: id книги по каталогу.
    :param comment: Текст комментария от пользователя.
    :param session: Сессия БД.
    :return: Сообщение - комментаций добавлен.
    """

    new_comment = Comment(content=comment.content, user_id=user.id, book_id=book_id)

    session.add(new_comment)

    await session.commit()
    await session.close()

    return {'Комментарий добавлен'}
