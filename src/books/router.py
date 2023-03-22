from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from src.auth.dependencies import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession

import src.books.schema as book_schema
from src.db import get_async_session
from .models import Comment
from .service import get_books_list, get_book_data, _update_comment, get_authors_list, get_author_book_list, _set_rating
from ..auth.models import User

router = APIRouter(
    prefix='/library',
    tags=['Book']
)


@router.get('/',
            response_model=List[book_schema.BooksSchema],
            status_code=status.HTTP_200_OK)
async def get_books(
        filter_str: str = '',
        limmit: int = 20,
        offset: int = 0,
        session: AsyncSession = Depends(get_async_session)
):
    """
    Эндпоинт всех книг. Пагинация, по умолчанию 10.
    :param filter_str: Искомое в названии или описании значение.
    :param limmit: Кол-во выводимых книг.
    :param offset: Номер набора по limmit.
    :param session: сессия БД
    :return: Книга: id, название, авторы, год, средний рейтинг, кол-во коментариев, теги
    """
    books = await get_books_list(filter_str, session)
    return books[offset:][:limmit]


@router.get('/{book_id}',
            response_model=book_schema.BookSchema,
            status_code=status.HTTP_200_OK)
async def get_book(
        book_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    """
    Энедпоин одной книги.
    :param book_id: id по каталогу
    :param session: сессия БД
    :return: Книга: id, название, авторы, год, средний рейтинг, комментарии к книге, теги
    """
    book = await get_book_data(book_id, session)
    if not book:
        raise HTTPException(status_code=404, detail=f'Книга с id {book_id} не найдена.')
    return book


@router.get(path='/author/',
            response_model=List[book_schema.AuthorSchema],
            status_code=status.HTTP_200_OK)
async def get_authors(
        filter_str: str = '',
        limmit: int = 20,
        offset: int = 0,
        session: AsyncSession = Depends(get_async_session),
):
    authors = await get_authors_list(filter_str, session)
    return authors[offset:][:limmit]


@router.get('/author/{author_id}',
            response_model=List[book_schema.BooksSchema],
            status_code=status.HTTP_200_OK)
async def get_books_author(
        author_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    author = await get_author_book_list(author_id, session)
    return author


@router.post('/{book_id}/rating',
             response_model=book_schema.RatingBase,
             status_code=status.HTTP_201_CREATED)
async def set_rating(
        book_id: int,
        rating: book_schema.RatingBase,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(get_current_user)
):
    """
    Энепоин рейтинга книги от пользователя. Если ранее оченка ставила, то обновляет оценку.
    :param user: Пользователь.
    :param book_id: id книги по каталогу.
    :param rating: Рейтинг от пользователя.
    :param session: Сессия БД.
    :return: Сообщение - рейтинг учтен.
    """
    res = await _set_rating(book_id=book_id,
                            rating=rating,
                            session=session,
                            user=user)

    return res


@router.post('/{book_id}/comment',
             response_model=book_schema.CommentBase,
             status_code=status.HTTP_201_CREATED)
async def add_comment(
        book_id: int,
        comment: book_schema.CommentBase,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(get_current_user)
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
    return new_comment


@router.patch('/comment/{comment_id}',
              response_model=book_schema.CommentBase,
              status_code=status.HTTP_200_OK)
async def update_comment(
        comment_id: int,
        new_comment: book_schema.CommentBase,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(get_current_user)
):
    """
    Эндпоинт обновления комментария.
    :param comment_id: id комментария.
    :param new_comment: Новый комментарий.
    :param session: Сессия БД.
    :param user: Пользователь.
    :return: Комментарий
    """
    comment = await _update_comment(comment_id=comment_id,
                                    new_comment=new_comment,
                                    user=user,
                                    session=session)
    await session.commit()
    if not comment:
        raise HTTPException(status_code=404, detail=f'Комментарий с id {comment_id} не найден.')
    elif isinstance(comment, str):
        raise HTTPException(status_code=422, detail=comment)
    return comment
