from async_typer import AsyncTyper
import aiohttp
from http import HTTPStatus
from fastapi import Depends

from models.role import Role, association_table
from schemas.roles import DBRole
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from services.roles import find_role

from db.postgres import engine, dsn

from core.config import superuser_settings, API_URL, ADMIN_ROLES

app = AsyncTyper()

@app.async_command()
async def create_super(login: str = superuser_settings.login,
                       password: str = superuser_settings.password):
    print(dsn, API_URL)
    session_fastapi = aiohttp.ClientSession()
    users_url = API_URL + 'users'
    response = await session_fastapi.post(
            users_url + '/register/',
            json={
                'first_name': 'admin',
                'last_name': 'admin',
                'login': login,
                'password': password
            }
    )

    if (response.status == HTTPStatus.BAD_REQUEST):
        print('Суперпользователь уже существует.')
    else:

        response = await session_fastapi.post(
            users_url + '/login/',
            json={
                'login': login,
                'password': password,
            }
        )

        info = await response.json()
        access_token, refresh_token, user_id = (info['access_token'],
                                                info['refresh_token'],
                                                info['id'])
        db = AsyncSession(bind=engine)

        for role in ADMIN_ROLES:
            new_role = Role(title=role)
            db.add(new_role)

            await db.commit()
            role_id = await find_role(db, role)
            await db.execute(insert(association_table).
                             values(user_id=user_id, role_id=role_id))
            await db.commit()
            await db.aclose()
        print('Суперпользователь %s создан (логин и пароль взяты из .env).' % (login))
        print('Access Token:', access_token)
        print('Refresh Token', refresh_token)
    await session_fastapi.close()


if __name__ == "__main__":
    app()
