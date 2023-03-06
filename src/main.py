import uvicorn
from fastapi import FastAPI

from src.books.router import router as router_books
from src.books.router_admin import router as router_books_admin
from src.users.schema import UserRead, UserCreate, UserUpdate
from src.users.auth_config import fastapi_users, auth_backend

app = FastAPI(
    title='Library fastapi'
)

app.include_router(
    router=router_books
)

app.include_router(
    router=router_books_admin
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
