import inspect

import factory
from factory import fuzzy
from factory.alchemy import SESSION_PERSISTENCE_FLUSH, SESSION_PERSISTENCE_COMMIT

from src.auth.models import User
from src.books.models import Book, Author, Tag
from .conftest import async_session_maker


class AsyncFactory(factory.alchemy.SQLAlchemyModelFactory):

    @classmethod
    async def _create(cls, model_class, *args, **kwargs):
        session = cls._meta.sqlalchemy_session
        for key, value in kwargs.items():
            if inspect.isawaitable(value):
                kwargs[key] = await value
            if isinstance(value, list) and value:
                kwargs[key] = [await session.merge(obj) for obj in value]
        return await cls._save(model_class, session, args, kwargs)

    @classmethod
    async def create_batch(cls, size, **kwargs):
        return [await cls.create(**kwargs) for _ in range(size)]

    @classmethod
    async def _save(cls, model_class, session, args, kwargs):
        session_persistence = cls._meta.sqlalchemy_session_persistence
        obj = model_class(*args, **kwargs)
        session.add(obj)
        if session_persistence == SESSION_PERSISTENCE_FLUSH:
            await session.flush()
        elif session_persistence == SESSION_PERSISTENCE_COMMIT:
            await session.commit()
        return obj


class UserFactory(AsyncFactory):
    class Meta:
        model = User
        sqlalchemy_session = async_session_maker()
        sqlalchemy_session_persistence = "commit"

    email = 'email@gmail.com'
    username = 'testuser'
    hashed_password = 'somepassword'


class AuthorFactory(AsyncFactory):
    class Meta:
        model = Author
        sqlalchemy_session = async_session_maker()
        sqlalchemy_session_persistence = "commit"

    name = factory.Sequence(lambda n: f'Author {n}')


class TagFactory(AsyncFactory):
    class Meta:
        model = Tag
        sqlalchemy_session = async_session_maker()
        sqlalchemy_session_persistence = "commit"

    content = fuzzy.FuzzyText(length=70)


class BookFactory(AsyncFactory):
    class Meta:
        model = Book
        sqlalchemy_session = async_session_maker()
        sqlalchemy_session_persistence = "commit"

    title = factory.Sequence(lambda n: f'Book {n}')
    year_published = factory.fuzzy.FuzzyInteger(1800, 2020)
    description = factory.fuzzy.FuzzyText(length=250)
    quantity = 10
    available = quantity
    authors = []
