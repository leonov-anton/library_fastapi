import asyncio

from src.db import async_session_maker

from src.books.models import Book, Author

books = {
    'book_1': Book(
        title='Война и мир',
        year_published=1869,
        description='Описание Война и мир',
        quantity=10
    ),
    'book_2': Book(
        title='Анна Каренина',
        year_published=1877,
        description='Описание Анна Каренина',
        quantity=10
    ),
    'book_3': Book(
        title='Воскресение',
        year_published=1899,
        description='Описание Воскресение',
        quantity=5
    ),
    'book_4': Book(
        title='И бегемоты сварились в своих бассейнах',
        year_published=1945,
        description='Описание И бегемоты сварились в своих бассейнах',
        quantity=5
    ),
    'book_5': Book(
        title='Защита Лужина',
        year_published=1930,
        description='Описание Защита Лужина',
        quantity=5
    )
}

authors = {
    'author_1': Author(
        name='Лев Толстой'
    ),
    'author_2': Author(
        name='Джек Керуак'
    ),
    'author_3': Author(
        name='Уильям Бурроуз'
    ),
    'author_4': Author(
        name='Александр Пушкин'
    )
}


async def fill_db(books: dict, authors: dict):
    async with async_session_maker() as session:

        books['book_1'].authors.append(authors['author_1'])
        books['book_2'].authors.append(authors['author_1'])
        books['book_3'].authors.append(authors['author_1'])
        books['book_4'].authors.append(authors['author_2'])
        books['book_4'].authors.append(authors['author_3'])
        books['book_5'].authors.append(authors['author_4'])

        for book in books.values():
            session.add(book)
        for author in authors.values():
            session.add(author)

        await session.commit()
        await session.close()


asyncio.run(fill_db(books, authors))
