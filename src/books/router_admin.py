from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import src.books.schema as book_schema
from src.db import get_async_session
from src.users.auth_config import fastapi_users
from src.users.models import User
from .service import (get_books_list,
                      add_new_book,
                      get_book_data,
                      change_book_data,
                      create_author,
                      change_author_data)

router = APIRouter(
    prefix='/library/admin',
    tags=['Book Admin']
)

# TODO:
#  эндпоинт удаление автора,
#  эндпоинты тега (CRUD),
#  эндпоинт изменение авторов книги,
#  эндпоинт изменение тегов книги.
#  эндпоинт выдачи книги пользователю
#  эндпоинт приема книги от пользователя


@router.get('/', response_model=List[book_schema.BooksAdminSchema])
async def get_books(
        limmit: int = 20,
        offset: int = 0,
        session: AsyncSession = Depends(get_async_session),
        admin: User = Depends(fastapi_users.current_user(active=True, superuser=True))
):
    books = await get_books_list(session)
    return books[offset:][:limmit]


@router.post('/', response_model=book_schema.BookAdminSchema)
async def add_book(
        book_data: book_schema.BookAdminSchema,
        authors_id: List[int],
        session: AsyncSession = Depends(get_async_session),
        admin: User = Depends(fastapi_users.current_user(active=True, superuser=True))
):
    book = await add_new_book(book_data, authors_id, session)
    return book


@router.get('/{boo_id}', response_model=book_schema.BookAdminSchema)
async def get_book(
        book_id: int,
        session: AsyncSession = Depends(get_async_session),
        admin: User = Depends(fastapi_users.current_user(active=True, superuser=True))
):
    book = await get_book_data(book_id, session)
    return book


@router.put('/{boo_id}', response_model=book_schema.BookAdminSchema)
async def patch_book(
        book_id: int,
        new_book_data: book_schema.BookAdminSchema,
        session: AsyncSession = Depends(get_async_session),
        admin: User = Depends(fastapi_users.current_user(active=True, superuser=True))
):
    book = await change_book_data(book_id, new_book_data, session)
    return book


@router.delete('/{boo_id}')
async def delete_book(
        book_id: int,
        session: AsyncSession = Depends(get_async_session),
        admin: User = Depends(fastapi_users.current_user(active=True, superuser=True))
):

    book = await get_book_data(book_id, session)
    await session.delete(book)
    await session.commit()
    return {'Message': 'Книга удалена'}


@router.post('/author', response_model=book_schema.AuthorBase)
async def add_author(
        author_name: str,
        session: AsyncSession = Depends(get_async_session),
        admin: User = Depends(fastapi_users.current_user(active=True, superuser=True))
):
    author = await create_author(author_name, session)
    return author


@router.patch('/author/{author_id}', response_model=book_schema.AuthorBase)
async def update_author(
        author_id: int,
        new_author_data: book_schema.AuthorBase,
        session: AsyncSession = Depends(get_async_session),
        admin: User = Depends(fastapi_users.current_user(active=True, superuser=True))
):
    author = await change_author_data(author_id, new_author_data, session)
    return author
