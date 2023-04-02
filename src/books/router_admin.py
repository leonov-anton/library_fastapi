from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

import src.books.schema as book_schema
from src.auth.dependencies import get_current_admin_user
from src.auth.models import User
from src.db import get_async_session
from .models import Book, Author, Tag
from .service import (
    get_books_list,
    add_new_book,
    get_book_data,
    update_book_data,
    create_author,
    change_author_data,
    add_new_tag,
    get_tags_list,
    change_instance,
    delete_instance,
    _give_book_to_user,
    _get_book_from_user,
)

router = APIRouter(
    prefix='/library/admin',
    tags=['Book Admin']
)


@router.get('/',
            response_model=List[book_schema.BooksAdminSchema],
            status_code=status.HTTP_200_OK)
async def get_books(
        filter_str: str = '',
        limmit: int = 20,
        offset: int = 0,
        session: AsyncSession = Depends(get_async_session),
        admin: User = Depends(get_current_admin_user)
):
    books = await get_books_list(filter_str, session)
    return books[offset:][:limmit]


@router.post('/',
             response_model=book_schema.BookAdminSchema,
             status_code=status.HTTP_201_CREATED)
async def add_book(
        book_data: book_schema.BookUpdateSchema,
        session: AsyncSession = Depends(get_async_session),
        admin: User = Depends(get_current_admin_user)
):
    book = await add_new_book(book_data, session)
    return book


@router.get('/{book_id}',
            response_model=book_schema.BookAdminSchema,
            status_code=status.HTTP_200_OK)
async def get_book(
        book_id: int,
        session: AsyncSession = Depends(get_async_session),
        admin: User = Depends(get_current_admin_user)
):
    return await get_book_data(book_id, session)


@router.patch('/{book_id}',
              response_model=book_schema.BookAdminSchema,
              status_code=status.HTTP_200_OK)
async def patch_book(
        book_id: int,
        new_book_data: book_schema.BookUpdateSchema,
        session: AsyncSession = Depends(get_async_session),
        admin: User = Depends(get_current_admin_user)
):
    return await update_book_data(book_id, new_book_data, session)


@router.delete('/{book_id}',
               status_code=status.HTTP_200_OK)
async def delete_book(
        book_id: int,
        session: AsyncSession = Depends(get_async_session),
        admin: User = Depends(get_current_admin_user)
):
    await delete_instance(book_id, Book, session)
    return {'Message': 'Object was deleted.'}


@router.post('/{book_id}/give',
             response_model=book_schema.BookBase,
             status_code=status.HTTP_200_OK)
async def give_book_to_user(
        book_id: int,
        user_id: int,
        session: AsyncSession = Depends(get_async_session),
        admin: User = Depends(get_current_admin_user)
):
    res = await _give_book_to_user(book_id, user_id, session)
    return res


@router.post('/{book_id}/get',
             response_model=book_schema.BookBase,
             status_code=status.HTTP_200_OK)
async def get_book_from_user(
        book_id: int,
        user_id: int,
        session: AsyncSession = Depends(get_async_session),
        admin: User = Depends(get_current_admin_user)
):
    res = await _get_book_from_user(book_id, user_id, session)
    return res


@router.post('/author',
             response_model=book_schema.AuthorBase,
             status_code=status.HTTP_201_CREATED)
async def add_author(
        author_name: str,
        session: AsyncSession = Depends(get_async_session),
        admin: User = Depends(get_current_admin_user)
):
    author = await create_author(author_name, session)
    return author


@router.patch('/author/{author_id}',
              response_model=book_schema.AuthorBase,
              status_code=status.HTTP_200_OK)
async def update_author(
        author_id: int,
        new_author_data: book_schema.AuthorBase,
        session: AsyncSession = Depends(get_async_session),
        admin: User = Depends(get_current_admin_user)
):
    author = await change_author_data(author_id, new_author_data, session)
    return author


@router.delete('/author/{author_id}',
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_author(
        author_id: int,
        session: AsyncSession = Depends(get_async_session),
        admin: User = Depends(get_current_admin_user)
):
    await delete_instance(author_id, Author, session)
    return {'Message': 'Object was deleted.'}


@router.get('/tag/',
            response_model=List[book_schema.TagSchema],
            status_code=status.HTTP_200_OK)
async def get_tags(
        limmit: int = 20,
        offset: int = 0,
        session: AsyncSession = Depends(get_async_session),
        admin: User = Depends(get_current_admin_user)
):
    tags = await get_tags_list(session)
    return tags[offset:][:limmit]


@router.post('/tag/',
             response_model=book_schema.TagBase,
             status_code=status.HTTP_201_CREATED)
async def add_tag(
        content: book_schema.TagBase,
        session: AsyncSession = Depends(get_async_session),
        admin: User = Depends(get_current_admin_user)
):
    tag = await add_new_tag(content, session)
    return tag


@router.patch('/tag/{tag_id}',
              response_model=book_schema.TagBase,
              status_code=status.HTTP_200_OK)
async def update_tag(
        tag_id: int,
        content: book_schema.TagBase,
        session: AsyncSession = Depends(get_async_session),
        admin: User = Depends(get_current_admin_user)
):
    tag = await change_instance(instance_id=tag_id, new_instance_data=content, model=Tag, session=session)
    await session.commit()
    return tag


@router.delete('/tag/{tag_id}',
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
        tag_id: int,
        session: AsyncSession = Depends(get_async_session),
        admin: User = Depends(get_current_admin_user)
):
    res = await delete_instance(tag_id, Tag, session)
    return {'Message': 'Object was deleted.'}
