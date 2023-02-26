from typing import List, Union

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, with_expression

import src.books.schema as book_schema
from src.db import get_async_session
from src.users.models import User
from src.users.auth_config import fastapi_users
from .models import Book, Rating, Comment

from .service import get_books_list, get_book_data

router = APIRouter(
    prefix='/library',
    tags=['Book']
)

# TODO:
#  энепоинт поиск книг по базе (название книги, описание, авторы),
#  энепоинт авторов (список с книгами),
#  энепоинт автора (список книг по одному автору)
#  энепоинт патч коммента


@router.get('/', response_model=List[book_schema.BooksSchema])
async def get_books(limmit: int = 20,
                    offset: int = 0,
                    session: AsyncSession = Depends(get_async_session),
                    ):
    """
    Эндпоинт всех книг. Пагинация, по умолчанию 10.
    :param limmit: Кол-во выводимых книг.
    :param offset: Номер набора по limmit.
    :param session: сессия БД
    :return: Книга: id, название, авторы, год, средний рейтинг, кол-во коментариев, теги
    """
    books = await get_books_list(session)
    return books[offset:][:limmit]


@router.get('/{book_id}', response_model=book_schema.BookSchema)
async def get_book(book_id: int,
                   session: AsyncSession = Depends(get_async_session)
                   ):
    """
    Энедпоин одной книги.
    :param book_id: id по каталогу
    :param session: сессия БД
    :return: Книга: id, название, авторы, год, средний рейтинг, комментарии к книге, теги
    """
    book = await get_book_data(book_id, session)
    return book


@router.post('/{book_id}/rating')
async def set_rating(book_id: int,
                     rating: book_schema.BookRating,
                     session: AsyncSession = Depends(get_async_session),
                     user: User = Depends(fastapi_users.current_user())
                     ):
    """
    Энепоин рейтинга книги от пользователя. Если ранее оченка ставила, то обновляет оченку.
    :param user: Пользователь.
    :param book_id: id книги по каталогу.
    :param rating: Рейтинг от пользователя.
    :param session: Сессия БД.
    :return: Сообщение - рейтинг учтен.
    """

    query = select(Rating).where(Rating.user == user, Rating.book_id == book_id)
    exist_rating = await session.scalar(query)

    if exist_rating:
        exist_rating.value = rating.value
        msg = 'обновлена'
    else:
        new_rating = Rating(value=rating.value, book_id=book_id, user_id=user.id)
        session.add(new_rating)
        msg = 'учтена'

    await session.commit()
    await session.close()

    return {'Message': f'{user.username}, ваша оценка {msg}!'}


@router.post('/{book_id}/comment')
async def add_comment(book_id: int,
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

    new_comment = Comment(content=comment.content, user=user, book_id=book_id)

    session.add(new_comment)

    await session.commit()
    await session.close()

    return {'Message': 'Комментарий добавлен!'}
