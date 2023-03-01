from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

import src.books.schema as book_schema
from src.db import get_async_session
from src.users.auth_config import fastapi_users
from src.users.models import User

from .models import Book, Rating, Comment, Author, Tag

from .service import (
    get_books_list,
    add_new_book,
    get_book_data,
    change_book_data,
    create_author,
    change_author_data,
    get_author_data,
    add_new_tag,
    get_tags_list,
    change_tag_data,
    change_instance,
    delete_instance,
    _give_book_to_user,
    _get_book_from_user,
    set_book_authors,
)

router = APIRouter(
    prefix='/library/admin',
    tags=['Book Admin']
)

# TODO:
#  изменять авторов и теги при измении книги.


@router.get('/',
            response_model=List[book_schema.BooksAdminSchema],
            status_code=status.HTTP_200_OK)
async def get_books(
        limmit: int = 20,
        offset: int = 0,
        session: AsyncSession = Depends(get_async_session),
        admin: User = Depends(fastapi_users.current_user(active=True, superuser=True))
):
    books = await get_books_list(session)
    return books[offset:][:limmit]


@router.post('/',
             response_model=book_schema.BookAdminSchema,
             status_code=status.HTTP_201_CREATED)
async def add_book(
        book_data: book_schema.BookAdminSchema,
        authors_id: List[int],
        session: AsyncSession = Depends(get_async_session),
        admin: User = Depends(fastapi_users.current_user(active=True, superuser=True))
):
    book = await add_new_book(book_data, authors_id, session)
    return book


@router.get('/{book_id}',
            response_model=book_schema.BookAdminSchema,
            status_code=status.HTTP_200_OK)
async def get_book(
        book_id: int,
        session: AsyncSession = Depends(get_async_session),
        admin: User = Depends(fastapi_users.current_user(active=True, superuser=True))
):
    book = await get_book_data(book_id, session)
    return book


@router.post('/{book_id}/give',
             response_model=book_schema.BookBase,
             status_code=status.HTTP_200_OK)
async def give_book_to_user(
        book_id: int,
        user_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    res = await _give_book_to_user(book_id, user_id, session)

    if not res:
        raise HTTPException(status_code=404, detail=f'Книга или пользователь не найден.')
    elif isinstance(res, str):
        raise HTTPException(status_code=404, detail=res)
    return res


@router.post('/{book_id}/get',
             response_model=book_schema.BookBase,
             status_code=status.HTTP_200_OK)
async def get_book_from_user(
        book_id: int,
        user_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    res = await _get_book_from_user(book_id, user_id, session)

    if not res:
        raise HTTPException(status_code=404, detail=f'Книга или пользователь не найден.')
    return res


@router.patch('/{book_id}',
              response_model=book_schema.BookAdminSchema,
              status_code=status.HTTP_200_OK)
async def patch_book(
        book_id: int,
        new_book_data: book_schema.BookPatchSchema,
        session: AsyncSession = Depends(get_async_session),
        admin: User = Depends(fastapi_users.current_user(active=True, superuser=True))
):
    book = await change_book_data(book_id, new_book_data, session)
    await session.commit()
    return book


@router.delete('/{book_id}',
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
        book_id: int,
        session: AsyncSession = Depends(get_async_session),
        admin: User = Depends(fastapi_users.current_user(active=True, superuser=True))
):

    book = await get_book_data(book_id, session)
    await session.delete(book)
    await session.commit()
    return HTTPException(status_code=204, detail='Книга удалена')


@router.patch('/{book_id}/authors', response_model=book_schema.BookAdminSchema, status_code=status.HTTP_200_OK)
async def update_book_authors(
        book_id: int,
        author_ids: List[int],
        session: AsyncSession = Depends(get_async_session),
        admin: User = Depends(fastapi_users.current_user(active=True, superuser=True))
):
    book = await set_book_authors(book_id, author_ids, session)
    await session.commit()
    if not book:
        raise HTTPException(status_code=404, detail=f'Книга с id {book_id} не найдена.')
    return book


@router.post('/author',
             response_model=book_schema.AuthorBase,
             status_code=status.HTTP_201_CREATED)
async def add_author(
        author_name: str,
        session: AsyncSession = Depends(get_async_session),
        admin: User = Depends(fastapi_users.current_user(active=True, superuser=True))
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
        admin: User = Depends(fastapi_users.current_user(active=True, superuser=True))
):
    author = await change_author_data(author_id, new_author_data, session)
    await session.commit()
    if not author:
        raise HTTPException(status_code=404, detail=f'Автор с id {author_id} не найден.')
    elif isinstance(author, str):
        raise HTTPException(status_code=422, detail=author)
    return author


@router.delete('/author/{author_id}',
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_author(
        author_id: int,
        session: AsyncSession = Depends(get_async_session),
        admin: User = Depends(fastapi_users.current_user(active=True, superuser=True))
):
    author = await get_author_data(author_id, session)
    if not author:
        raise HTTPException(status_code=404, detail=f'Автор с id {author_id} не найден.')

    await session.delete(author)
    await session.commit()
    return 'Автор удален.'


@router.get('/tag',
            response_model=List[book_schema.TagSchema],
            status_code=status.HTTP_200_OK)
async def get_tags(
        limmit: int = 20,
        offset: int = 0,
        session: AsyncSession = Depends(get_async_session),
        admin: User = Depends(fastapi_users.current_user(active=True, superuser=True))
):
    tags = get_tags_list(session)
    return tags[offset:][:limmit]


@router.post('/tag',
             response_model=book_schema.TagBase,
             status_code=status.HTTP_201_CREATED)
async def add_tag(
        content: book_schema.TagBase,
        session: AsyncSession = Depends(get_async_session),
        # admin: User = Depends(fastapi_users.current_user(active=True, superuser=True))
):
    tag = await add_new_tag(content, session)
    if not tag:
        raise HTTPException(status_code=422, detail='Данные не переданы')
    return tag


@router.patch('/tag/{id}',
              response_model=book_schema.TagBase,
              status_code=status.HTTP_200_OK)
async def update_tag(
        tag_id: int,
        content: book_schema.TagBase,
        session: AsyncSession = Depends(get_async_session),
        admin: User = Depends(fastapi_users.current_user(active=True, superuser=True))
):
    tag = await change_instance(instance_id=tag_id, new_instance_data=content, model=Tag, session=session)
    await session.commit()
    if not tag:
        raise HTTPException(status_code=404, detail=f'Тег с id {tag_id} не найден.')
    elif isinstance(tag, str):
        raise HTTPException(status_code=422, detail=tag)
    return tag


@router.delete('/tag/{id}',
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
        tag_id: int,
        session: AsyncSession = Depends(get_async_session),
        admin: User = Depends(fastapi_users.current_user(active=True, superuser=True))
):
    res = await delete_instance(tag_id, Tag, session)

    if not res:
        raise HTTPException(status_code=404, detail=f'Тег с id {tag_id} не найден.')
    return 'Тег удален.'
