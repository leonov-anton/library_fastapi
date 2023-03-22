import pytest
from httpx import AsyncClient
from .factories import BookFactory, AuthorFactory, UserFactory


class TestGetBooks:
    endpoint = '/library/'

    @pytest.mark.asyncio
    async def test_get_books(self, get_test_client: AsyncClient):
        authors = await AuthorFactory.create_batch(2)
        await BookFactory.create_batch(3, authors=authors)
        await BookFactory.create(authors=[authors[0]])
        await BookFactory.create(authors=[authors[1]])

        response = await get_test_client.get(self.endpoint)

        assert response.status_code == 200
        assert len(response.json()) == 5
        assert response.json()[0]['title'] == 'Book 0'

    @pytest.mark.asyncio
    async def test_get_books_search(self, get_test_client: AsyncClient):
        response = await get_test_client.get(self.endpoint,
                                             params={'filter_str': '1'})

        assert response.status_code == 200
        assert response.json()[0]['title'] == 'Book 1'


class TestGetAuthors:
    endpoint = '/library/author/'

    @pytest.mark.asyncio
    async def test_get_authors(self, get_test_client: AsyncClient):
        response = await get_test_client.get(self.endpoint)

        assert response.status_code == 200
        assert len(response.json()) == 2

    @pytest.mark.asyncio
    async def test_get_authors_search(self, get_test_client: AsyncClient):
        response = await get_test_client.get(self.endpoint,
                                             params={'filter_str': '1'})
        assert response.status_code == 200
        assert response.json()[0]['name'] == 'Author 1'


class TestGetBooksAuthor:
    @pytest.mark.asyncio
    async def test_get_books_author(self, get_test_client: AsyncClient):
        response = await get_test_client.get('/library/author/1')

        assert response.status_code == 200
        assert len(response.json()) == 4

    @pytest.mark.asyncio
    async def test_get_books_author_not_exists(self, get_test_client: AsyncClient):
        response = await get_test_client.get('/library/author/111')

        assert response.status_code == 200
        assert len(response.json()) == 0

class TestRating:
    endpoint = '/library/1/rating'

    @pytest.mark.asyncio
    async def test_set_rating(self, get_test_client: AsyncClient, access_login_user: str):
        response = await get_test_client.post(self.endpoint,
                                              cookies={'access_token': access_login_user},
                                              json={'value': 4})
        assert response.status_code == 201
        assert response.json()['value'] == 4

    @pytest.mark.asyncio
    async def test_reset_rating(self, get_test_client: AsyncClient, access_login_user: str):
        response = await get_test_client.post(self.endpoint,
                                              cookies={'access_token': access_login_user},
                                              json={'value': 5})
        assert response.status_code == 201
        assert response.json()['value'] == 5

    @pytest.mark.asyncio
    async def test_set_rating_no_data(self, get_test_client: AsyncClient, access_login_user: str):
        response = await get_test_client.post(self.endpoint,
                                              cookies={'access_token': access_login_user})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_set_rating_no_user(self, get_test_client: AsyncClient):
        response = await get_test_client.post(self.endpoint,
                                              json={'value': 5})
        assert response.status_code == 401


class TestCreateComment:
    endpoint = '/library/1/comment'

    @pytest.mark.asyncio
    async def test_create_comment(self, get_test_client: AsyncClient, access_login_user: str):
        response = await get_test_client.post(self.endpoint,
                                              cookies={'access_token': access_login_user},
                                              json={'content': 'test comment'})

        assert response.status_code == 201
        assert response.json()['content'] == 'test comment'

    @pytest.mark.asyncio
    async def test_create_comment_no_user(self, get_test_client: AsyncClient):
        response = await get_test_client.post(self.endpoint,
                                              json={'content': 'test comment'})

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_comment_no_data(self, get_test_client: AsyncClient, access_login_user: str):
        response = await get_test_client.post(self.endpoint,
                                              cookies={'access_token': access_login_user})

        assert response.status_code == 422


class TestUpdateComment:
    endpoint = '/library/comment/1'

    @pytest.mark.asyncio
    async def test_update_comment(self, get_test_client: AsyncClient, access_login_user: str):
        response = await get_test_client.patch('/library/comment/1',
                                               cookies={'access_token': access_login_user},
                                               json={'content': 'new test comment'})

        assert response.status_code == 200
        assert response.json()['content'] == 'new test comment'

    @pytest.mark.asyncio
    async def test_update_comment_another_user(self, get_test_client: AsyncClient, access_login_another_user: str):
        await UserFactory.create(username='another_user',
                                 email='another_user@mail.com',
                                 hashed_password=b'101100101110101110011')
        response = await get_test_client.patch('/library/comment/1',
                                               cookies={'access_token': access_login_another_user},
                                               json={'content': 'new test comment'})

        assert response.status_code == 422
        assert response.json()['detail'] == 'Комметрий оставлен другим пользователем.'

    @pytest.mark.asyncio
    async def test_update_comment_not_exists(self, get_test_client: AsyncClient, access_login_user: str):
        response = await get_test_client.patch('/library/comment/777',
                                               cookies={'access_token': access_login_user},
                                               json={'content': 'new test comment'})

        assert response.status_code == 404
        assert response.json()['detail'] == 'Комментарий с id 777 не найден.'


class TestGetBook:
    @pytest.mark.asyncio
    async def test_get_book(self, get_test_client: AsyncClient):
        response = await get_test_client.get('/library/1')

        assert response.status_code == 200
        assert response.json()['title'] == 'Book 0'
        assert response.json()['comments'][0]['content'] == 'new test comment'
        assert response.json()['comments'][0]['id'] == 1
        assert response.json()['avg_rating'] == 5

    @pytest.mark.asyncio
    async def test_get_wrong_book(self, get_test_client: AsyncClient):
        response = await get_test_client.get('/library/777')

        assert response.status_code == 404
