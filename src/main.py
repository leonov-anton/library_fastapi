import uvicorn
from fastapi import FastAPI

from src.books.router import router as router_books
from src.books.router_admin import router as router_books_admin
from src.auth.router import router as router_auth

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
    router=router_auth
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
