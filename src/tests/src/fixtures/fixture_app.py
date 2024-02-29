import pytest

from core.config import superuser_settings

from httpx import AsyncClient
from settings import API_USERS


@pytest.fixture
async def admin_tokens():
    async with AsyncClient(base_url=API_USERS) as client:
        user_login_data = {
            'login': superuser_settings.login,
            'password': superuser_settings.password
        }

        response = await client.post('login/', json=user_login_data)

    return response.json()
