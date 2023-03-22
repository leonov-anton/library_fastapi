from datetime import datetime

from sqlalchemy import String, Boolean, Column, Integer, TIMESTAMP, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship

from src.db import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(320), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(LargeBinary, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    register_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)

    books = relationship('Book', secondary='book_user', back_populates='users')
    comments = relationship('Comment', back_populates='user')
    ratings = relationship('Rating', back_populates='user')


class AuthRefreshToken(Base):
    __tablename__ = 'auth_refresh_token'

    id = Column(Integer, primary_key=True, index=True)
    refresh_token = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    expires_at = Column(TIMESTAMP, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
