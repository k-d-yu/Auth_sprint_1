from http import HTTPStatus
import pytest

from httpx import AsyncClient
from settings import API_ROLES


@pytest.mark.asyncio
async def test_create_role(admin_tokens):
    headers = {'Authorization': '{token}'.format(token=admin_tokens['access_token'])}
    params = {'role_title': 'test_role'}
    async with AsyncClient(base_url=API_ROLES) as client:
        response = await client.post('create/', params=params, headers=headers)

        assert response.status_code == HTTPStatus.CREATED


@pytest.mark.asyncio
async def test_list_roles():
    async with AsyncClient(base_url=API_ROLES) as client:
        response = await client.post('get/')

        assert response.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_update_role(admin_tokens):
    headers = {'Authorization': '{token}'.format(token=admin_tokens['access_token'])}
    params = {'title': 'test_role',
              'change_to': 'test_role_2'}
    async with AsyncClient(base_url=API_ROLES) as client:
        response = await client.post('update/', params=params, headers=headers)

    assert response.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_delete_role(admin_tokens):
    headers = {'Authorization': '{token}'.format(token=admin_tokens['access_token'])}

    params = {'title': 'test_role_2'}
    async with AsyncClient(base_url=API_ROLES) as client:
        response = await client.post('delete/', params=params, headers=headers)

    assert response.status_code == HTTPStatus.OK
