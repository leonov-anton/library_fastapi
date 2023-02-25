from datetime import datetime

from sqlalchemy import Integer, String, ForeignKey, Table, Column, TIMESTAMP
from sqlalchemy.orm import relationship, Mapped, query_expression

from src.users.models import User

from src.db import Base

# Many-to-many table books-authors
book_author = Table(
    'book_author',
    Base.metadata,
    Column('book_id', ForeignKey('book.id'), primary_key=True),
    Column('author_id', ForeignKey('author.id'), primary_key=True),
)

# Many-to-many table books-comments
book_user = Table(
    'book_user',
    Base.metadata,
    Column('book_id', ForeignKey('book.id'), primary_key=True),
    Column('user_id', ForeignKey('user.id'), primary_key=True),
)

# Many-to-many table books-tags
book_tag = Table(
    'book_tag',
    Base.metadata,
    Column('book_id', ForeignKey('book.id'), primary_key=True),
    Column('tag_id', ForeignKey('tag.id'), primary_key=True),
)


class Author(Base):
    __tablename__ = 'author'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    books = relationship('Book', secondary='book_author', back_populates='authors')


class Book(Base):
    __tablename__ = 'book'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    year_published = Column(Integer)
    description = Column(String(250), nullable=True)
    quantity = Column(Integer, nullable=False)
    available = Column(Integer)

    authors = relationship('Author', secondary='book_author', back_populates='books')
    users = relationship('User', secondary='book_user', back_populates='books')

    comments = relationship('Comment', back_populates='book')
    count_comments = query_expression()

    tags = relationship('Tag', secondary='book_tag', back_populates='books')

    ratings = relationship('Rating', back_populates='book')
    avg_rating = query_expression()


class Comment(Base):
    __tablename__ = 'comment'

    id = Column(Integer, primary_key=True, index=True)
    created = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    content = Column(String(300))

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', back_populates='comments')

    book_id = Column(Integer, ForeignKey('book.id'))
    book = relationship('Book', back_populates='comments')


class Tag(Base):
    __tablename__ = 'tag'

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String(100))

    books = relationship('Book', secondary='book_tag', back_populates='tags')


class Rating(Base):
    __tablename__ = 'rating'

    id = Column(Integer, primary_key=True, index=True)
    value = Column(Integer)

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', back_populates='ratings')

    book_id = Column(Integer, ForeignKey('book.id'))
    book = relationship('Book', back_populates='ratings')
