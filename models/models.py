from datetime import datetime

from sqlalchemy import Integer, String, TIMESTAMP, ForeignKey, Table, Column, JSON, Boolean
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Many-to-many table books-authors
books_authors = Table(
    'books_authors',
    Base.metadata,
    Column('book_id', ForeignKey('book.id'), primary_key=True),
    Column('author_id', ForeignKey('author.id'), primary_key=True),
)

# Many-to-many table books-comments
books_users = Table(
    'books_users',
    Base.metadata,
    Column('book_id', ForeignKey('book.id'), primary_key=True),
    Column('user_id', ForeignKey('users.id'), primary_key=True),
)

# Many-to-many table books-tags
books_tags = Table(
    'books_tags',
    Base.metadata,
    Column('book_id', ForeignKey('book.id'), primary_key=True),
    Column('tag_id', ForeignKey('tags.id'), primary_key=True),
)


class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(10), nullable=False, unique=True)
    permissions = Column(JSON, nullable=True)

    users = relationship('User', back_populates='role')


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    registration_datetime = Column('registration_datetime', TIMESTAMP, default=datetime.utcnow)

    role_id = Column(Integer, ForeignKey('roles.id'))
    role = relationship('Role', back_populates='users')

    books = relationship('Book', secondary='books_users', back_populates='users')

    comments = relationship('Comment', back_populates='user')

    ratings = relationship('Rating', back_populates='user')


class Author(Base):
    __tablename__ = 'autors'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)

    books = relationship('Book', secondary='books_authors', back_populates='authors')


class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    year_published = Column(Integer)
    description = Column(String(250), nullable=True)
    quantity = Column(Integer, nullable=False)
    available = Column(Integer)

    authors = relationship('Author', secondary='books_authors', back_populates='books')

    users = relationship('User', secondary='books_users', back_populates='books')

    comments = relationship('Comment', back_populates='book')

    tags = relationship('Tag', secondary='books_authors', back_populates='books')

    ratings = relationship('Rating', back_populates='book')


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String(300))

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='comments')

    book_id = Column(Integer, ForeignKey('books.id'))
    book = relationship('Book', back_populates='comments')


class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String(100))

    books = relationship('Book', secondary='books_tags', back_populates='tags')


class Rating(Base):
    __tablename__ = 'rating'

    id = Column(Integer, primary_key=True, index=True)
    value = Column(Integer)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='ratings')

    book_id = Column(Integer, ForeignKey('books.id'))
    book = relationship('Book', back_populates='ratings')
