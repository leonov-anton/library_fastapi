import pytest
from httpx import AsyncClient

from .factories import BookFactory

class TestCreateBook:
    endpoint = '/library/admin/'

    @pytest.mark.asyncio
    async def test_create_book_not_admin(self, get_test_client: AsyncClient, access_login_user: str):
        response = await get_test_client.post(self.endpoint,
                                              cookies={'access_token': access_login_user},
                                              json={'title': 'New book title',
                                                    'year_published': 2000,
                                                    'description': 'Some book description',
                                                    'authors_id': [1],
                                                    'quantity': 10})

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_book_wrong_year(self, get_test_client: AsyncClient, access_login_admin: str):
        response = await get_test_client.post(self.endpoint,
                                              cookies={'access_token': access_login_admin},
                                              json={'title': 'New book title',
                                                    'year_published': 3000,
                                                    'description': 'Some book description',
                                                    'authors_id': [1],
                                                    'quantity': 10})

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_book(self, get_test_client: AsyncClient, access_login_admin: str):
        response = await get_test_client.post(self.endpoint,
                                              cookies={'access_token': access_login_admin},
                                              json={'title': 'New book title',
                                                    'year_published': 2000,
                                                    'description': 'Some book description',
                                                    'authors_id': [1],
                                                    'quantity': 10})

        assert response.status_code == 201
        assert response.json()['title'] == 'New book title'


class TestUpdateBook:
    endpoint = '/library/admin/1'

    @pytest.mark.asyncio
    async def test_update_book_not_admin(self, get_test_client: AsyncClient, access_login_user: str):
        response = await get_test_client.patch(self.endpoint,
                                               cookies={'access_token': access_login_user},
                                               json={'title': 'New book 0 title'})
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_update_book(self, get_test_client: AsyncClient, access_login_admin: str):
        response = await get_test_client.patch(self.endpoint,
                                               cookies={'access_token': access_login_admin},
                                               json={'title': 'New book 0 title'})
        assert response.status_code == 200
        assert response.json()['title'] == 'New book 0 title'


class TestDeleteBook:
    endpoint = '/library/admin/2'

    @pytest.mark.asyncio
    async def test_delete_book_not_admin(self, get_test_client: AsyncClient, access_login_user: str):
        response = await get_test_client.delete(self.endpoint,
                                                cookies={'access_token': access_login_user})
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_delete_book(self, get_test_client: AsyncClient, access_login_admin: str):
        response = await get_test_client.delete(self.endpoint,
                                                cookies={'access_token': access_login_admin})
        assert response.status_code == 200
        assert response.json()['Success'] is True


class TestGiveBookToUser:
    endpoint = '/library/admin/1/give'

    @pytest.mark.asyncio
    async def test_give_book_to_user(self, get_test_client: AsyncClient, access_login_admin: str):
        response = await get_test_client.post(self.endpoint,
                                              cookies={'access_token': access_login_admin},
                                              params={'user_id': 1})
        assert response.status_code == 200
        assert response.json()['title'] == 'New book 0 title'

    @pytest.mark.asyncio
    async def test_give_book_to_user_not_exist(self, get_test_client: AsyncClient, access_login_admin: str):
        response = await get_test_client.post(self.endpoint,
                                              cookies={'access_token': access_login_admin},
                                              params={'user_id': 777})
        assert response.status_code == 404
        assert response.json()['detail'] == 'Пользователь не найден.'

    @pytest.mark.asyncio
    async def test_give_book_to_user_book_unavailable(self, get_test_client: AsyncClient, access_login_admin: str):
        book = await BookFactory.create(quantity=10, available=0)
        response = await get_test_client.post(f'/library/admin/{book.id}/give',
                                              cookies={'access_token': access_login_admin},
                                              params={'user_id': 1})
        assert response.status_code == 404
        assert response.json()['detail'] == 'Книги нет в наличии.'


class TestGetBookFromUser:
    endpoint = '/library/admin/1/get'

    @pytest.mark.asyncio
    async def test_get_book_from_user_not_taken(self, get_test_client: AsyncClient, access_login_admin: str):
        response = await get_test_client.post('/library/admin/5/get',
                                              cookies={'access_token': access_login_admin},
                                              params={'user_id': 1})
        assert response.status_code == 404
        assert response.json()['detail'] == 'Пользователь не брал эту кгину.'

    @pytest.mark.asyncio
    async def test_get_book_from_user(self, get_test_client: AsyncClient, access_login_admin: str):
        response = await get_test_client.post(self.endpoint,
                                              cookies={'access_token': access_login_admin},
                                              params={'user_id': 1})
        assert response.status_code == 200
        assert response.json()['title'] == 'New book 0 title'


class TestAddAuthor:
    endpoint = '/library/admin/author'

    @pytest.mark.asyncio
    async def test_add_author(self, get_test_client: AsyncClient, access_login_admin: str):
        response = await get_test_client.post(self.endpoint,
                                              cookies={'access_token': access_login_admin},
                                              params={'author_name': 'New Author'})
        assert response.status_code == 201


class TestUpdateAuthor:
    endpoint = '/library/admin/author/1'

    @pytest.mark.asyncio
    async def test_update_author(self, get_test_client: AsyncClient, access_login_admin: str):
        response = await get_test_client.patch('/library/admin/author/1',
                                               cookies={'access_token': access_login_admin},
                                               json={'name': 'New Author 1 Name'})
        assert response.status_code == 200


class TestDeleteAuthor:
    endpoint = '/library/admin/author/1'

    @pytest.mark.asyncio
    async def test_delete_author(self, get_test_client: AsyncClient, access_login_admin: str):
        response = await get_test_client.delete('/library/admin/author/1',
                                                cookies={'access_token': access_login_admin})
        assert response.status_code == 204


class TestAddTag:
    endpoint = '/library/admin/tag/'

    @pytest.mark.asyncio
    async def test_add_tag(self, get_test_client: AsyncClient, access_login_admin: str):
        response = await get_test_client.post(self.endpoint,
                                              cookies={'access_token': access_login_admin},
                                              json={'content': 'New tag'})
        assert response.status_code == 201
        assert response.json() == {'id': 1, 'content': 'New tag'}


class TestGetTags:
    endpoint = '/library/admin/tag/'

    @pytest.mark.asyncio
    async def test_get_tags(self, get_test_client: AsyncClient, access_login_admin: str):
        response = await get_test_client.get(self.endpoint,
                                             cookies={'access_token': access_login_admin})
        assert response.status_code == 200
        assert response.json()[0]['id'] == 1


class TestUpdateTag:
    endpoint = '/library/admin/tag/1'

    @pytest.mark.asyncio
    async def test_update_tag(self, get_test_client: AsyncClient, access_login_admin: str):
        response = await get_test_client.patch(self.endpoint,
                                               cookies={'access_token': access_login_admin},
                                               json={'content': 'New tag data'})
        assert response.status_code == 200
        assert response.json()['content'] == 'New tag data'


class TestDeleteTag:
    endpoint = '/library/admin/tag/1'

    @pytest.mark.asyncio
    async def test_delete_tag(self, get_test_client: AsyncClient, access_login_admin: str):
        response = await get_test_client.delete(self.endpoint,
                                                cookies={'access_token': access_login_admin})
        assert response.status_code == 204
