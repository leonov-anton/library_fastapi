from datetime import datetime

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import String, Boolean, Column, Integer, ForeignKey, TIMESTAMP, JSON
from sqlalchemy.orm import relationship

from src.db import Base


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(320), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    registration_datetime = Column(TIMESTAMP, default=datetime.utcnow)

    role_id = Column(Integer, ForeignKey('role.id'))
    role = relationship('Role', back_populates='user')

    books = relationship('Book', secondary='book_user', back_populates='users')

    comments = relationship('Comment', back_populates='users')

    ratings = relationship('Rating', back_populates='users')


class Role(Base):
    __tablename__ = 'role'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(10), nullable=False, unique=True)
    permissions = Column(JSON, nullable=True)

    users = relationship('User', back_populates='role')
