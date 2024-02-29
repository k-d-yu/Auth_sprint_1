import http
import pytest

from httpx import AsyncClient

from tests.settings import API_USERS
from tests.testdata.data import test_data


@pytest.mark.asyncio
async def test_register_user_new():
    async with AsyncClient(base_url=API_USERS) as client:
        user_data = {
            'login': test_data.login[0],
            'password': test_data.password[0],
            'first_name': test_data.first_name[0],
            'last_name': test_data.last_name[0]
        }
        response = await client.post('register/', json=user_data)

        assert response.status_code == http.HTTPStatus.OK

        data = response.json()

        assert data['login'] == user_data['login']
        assert data['first_name'] == user_data['first_name']
        assert data['last_name'] == user_data['last_name']


@pytest.mark.asyncio
async def test_register_user_old():
    async with AsyncClient(base_url=API_USERS) as client:
        user_data = {
            'login': test_data.login[0],
            'password': test_data.password[0],
            'first_name': test_data.first_name[0],
            'last_name': test_data.last_name[0]
        }

        response = await client.post('register/', json=user_data)

        assert response.status_code == http.HTTPStatus.BAD_REQUEST


@pytest.mark.asyncio
async def test_login_user():
    async with AsyncClient(base_url=API_USERS) as client:
        user_login_data = {
            'login': test_data.login[0],
            'password': test_data.password[0],
        }

        response = await client.post('login/', json=user_login_data)

        assert response.status_code == http.HTTPStatus.OK

        data = response.json()
        assert 'id' in data
        assert 'access_token' in data
        assert 'refresh_token' in data


@pytest.mark.asyncio
async def test_login_user_error_login():
    async with AsyncClient(base_url=API_USERS) as client:
        user_data = {
            'login': test_data.login_error[0],
            'password': test_data.password[0],
        }

        response = await client.post('login/', json=user_data)

        assert response.status_code == http.HTTPStatus.BAD_REQUEST


@pytest.mark.asyncio
async def test_login_user_error_password():
    async with AsyncClient(base_url=API_USERS) as client:
        user_data = {
            'login': test_data.login[0],
            'password': test_data.password_error[0],
        }

        response = await client.post('login/', json=user_data)

        assert response.status_code == http.HTTPStatus.BAD_REQUEST


@pytest.mark.asyncio
async def test_refresh_token():
    async with AsyncClient(base_url=API_USERS) as client:
        if test_data.user_id:
            response = await client.get('refresh-token/?user_id=' + test_data.user_id)

            assert response.status_code == http.HTTPStatus.OK

            data = response.json()

            assert 'login' in data
            assert 'id' in data
            assert 'access_token' in data


@pytest.mark.asyncio
async def test_logout_user():
    async with AsyncClient(base_url=API_USERS) as client:
        if test_data.user_id:
            response = await client.get('logout/?user_id=' + test_data.user_id)

            assert response.status_code == http.HTTPStatus.OK

            data = response.json()

            assert "message" in data
            assert data["message"] == "Пользователь успешно вышел из аккаунта."


@pytest.mark.asyncio
async def test_change_password():
    async with AsyncClient(base_url=API_USERS) as client:
        if test_data.user_id:
            change_password_data = {
                'current_password': test_data.current_password[0],
                'new_password': test_data.new_password[0]
            }

            response = await client.post('change-password/?user_id=' + test_data.user_id, json=change_password_data)
            assert response.status_code == http.HTTPStatus.OK

            data = response.json()
            assert "message" in data
            assert data["message"] == "Пароль успешно изменен"


@pytest.mark.asyncio
async def test_get_user_sessions():
    async with AsyncClient(base_url=API_USERS) as client:
        if test_data.user_id:
            page = 1
            page_size = 10

            response = await client.get(f"sessions/?user_id={test_data.user_id}&page={page}&page_size={page_size}")

            assert response.status_code == http.HTTPStatus.OK

            data = response.json()
            assert "sessions" in data
            assert "page" in data
            assert "page_size" in data
            assert "total_pages" in data
            assert "next_page" in data
            assert "previous_page" in data
