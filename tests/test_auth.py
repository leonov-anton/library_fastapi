import pytest
from httpx import AsyncClient


class TestRegistration:
    endpoint = '/auth/register'

    @pytest.mark.asyncio
    async def test_registration_weak_password(self, get_test_client: AsyncClient):
        response = await get_test_client.post(self.endpoint, json={
            "email": "user@example.com",
            "password": "weak_password",
            "username": "testuser"
        })
        assert response.status_code == 422
        assert response.json()['detail'][0]['msg'] == "Пароль должен содержать хоты бы " \
                                                      "одну строчку букву и заглавную букву (только латинские), " \
                                                      "цифру,символ из набора - !@#$%^&*"

    @pytest.mark.asyncio
    async def test_register(self, get_test_client: AsyncClient):
        response = await get_test_client.post(self.endpoint, json={
            "email": "user@example.com",
            "password": "Qwe123!",
            "username": "testuser"
        })
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_register_email_taken(self, get_test_client: AsyncClient):
        response = await get_test_client.post(self.endpoint, json={
            "email": "user@example.com",
            "password": "Qwe123!",
            "username": "testuser"
        })
        assert response.status_code == 400


class TestLogin:
    endpoint = '/auth/user/token'

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, get_test_client: AsyncClient):
        response = await get_test_client.post(self.endpoint, json={
            "email": "user@example.com",
            "password": "Sad987*",
        })
        assert response.status_code == 400
        assert response.json()['detail'] == 'Пользотавель с таким данными не зарегистрирован.'

    @pytest.mark.asyncio
    async def test_login(self, get_test_client: AsyncClient):
        response = await get_test_client.post(self.endpoint, json={
            "email": "user@example.com",
            "password": "Qwe123!",
        })

        assert response.status_code == 200
        assert response.cookies.get('access_token')
        assert response.cookies.get('refresh_token')


class TestRefreshTokens:
    endpoint = '/auth/user/token'

    @pytest.mark.asyncio
    async def test_refresh(self, get_test_client: AsyncClient, get_refresh_token_db: str):
        response = await get_test_client.put(self.endpoint,
                                             cookies={'refresh_token': get_refresh_token_db})
        assert response.status_code == 200
        assert response.cookies.get('access_token')
        assert response.cookies.get('refresh_token')

    @pytest.mark.asyncio
    async def test_refresh_wrong_token(self, get_test_client: AsyncClient):
        response = await get_test_client.put(self.endpoint,
                                             cookies={'refresh_token': 'wrong_token'})
        assert response.status_code == 400
        assert response.json()['detail'] == 'Неверный токен.'


class TestGetUser:
    endpoint = '/auth/user'

    @pytest.mark.asyncio
    async def test_get_user(self, get_test_client: AsyncClient, access_login_user: str):
        response = await get_test_client.get(self.endpoint,
                                             cookies={'access_token': access_login_user})

        assert response.status_code == 200
        assert response.json()['username'] == 'testuser'

    @pytest.mark.asyncio
    async def test_get_user_no_token(self, get_test_client: AsyncClient):
        response = await get_test_client.get(self.endpoint)
        assert response.status_code == 401
        assert response.json()['detail'] == 'Необходима аутентификация.'

    @pytest.mark.asyncio
    async def test_get_user_wrong_token(self, get_test_client: AsyncClient):
        response = await get_test_client.get(self.endpoint,
                                             cookies={'access_token': 'wrong_token'})
        assert response.status_code == 401
        assert response.json()['detail'] == 'Неверный токен.'


class TestLogout:
    endpoint = '/auth/user/token'

    @pytest.mark.asyncio
    async def test_logout(self, get_test_client: AsyncClient, get_refresh_token_db: str):
        response = await get_test_client.delete(self.endpoint,
                                                cookies={'refresh_token': get_refresh_token_db})
        assert response.status_code == 200
        assert response.json()['Message'] == 'Выход выполнен.'
        assert response.cookies.get('access_token', None) is None
        assert response.cookies.get('refresh_token', None) is None

    @pytest.mark.asyncio
    async def test_logout_no_token(self, get_test_client: AsyncClient):
        response = await get_test_client.delete(self.endpoint)
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_logout_wrong_token(self, get_test_client: AsyncClient):
        response = await get_test_client.delete(self.endpoint,
                                                cookies={'refresh_token': 'get_refresh_token_db'})
        assert response.status_code == 400
