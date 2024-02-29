from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from http import HTTPStatus

from schemas.roles import DBRole, DBUserRole
from sqlalchemy import delete, update, insert

from db.postgres import get_session
from models.role import Role, association_table
from core.decorators import admin_role_required

from services.roles import (find_role,
                            get_roles,
                            get_user_id,
                            get_roles_by_id,
                            get_roles_by_login)

app = APIRouter()
header_scheme = APIKeyHeader(name="Authorization", auto_error=False)


@app.post('/create/',
          response_model=DBRole,
          summary='создание роли',
          status_code=HTTPStatus.CREATED)
@admin_role_required
async def create_role(role_title: str,
                      request_header: str = Depends(header_scheme),
                      db: AsyncSession = Depends(get_session),
                      ):
    if await find_role(db, role_title):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail='Такая роль уже есть.')
    new_role = Role(title=role_title)
    db.add(new_role)
    await db.commit()
    return DBRole(**new_role.__dict__)


@app.patch('/update/',
           summary='обновление роли',
           status_code=HTTPStatus.OK)
@admin_role_required
async def delete_role(title: str,
                      change_to: str,
                      request_header: str = Depends(header_scheme),
                      db: AsyncSession = Depends(get_session)):
    if not (role := await find_role(db, title)):
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='Такой роли не существует.')
    await db.execute(update(Role).
                     where(Role.id == role[0].id).
                     values(title=change_to))
    await db.commit()
    return {'msg': 'Роль обновлена.'}


@app.delete('/delete/',
            summary='удаление роли',
            status_code=HTTPStatus.OK)
@admin_role_required
async def update_role(title: str,
                      request_header: str = Depends(header_scheme),
                      db: AsyncSession = Depends(get_session)):
    if not await find_role(db, title):
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='Такой роли не существует.')
    await db.execute(delete(Role).where(Role.title == title))
    await db.commit()
    return {'msg': 'Роль удалена.'}


@app.get('/get/',
         summary='получить список всех ролей',
         status_code=HTTPStatus.OK)
async def get(db: AsyncSession = Depends(get_session)):
    return await get_roles(db)


async def check_login_role(user_name: str,
                           role_title: str,
                           db: AsyncSession):
    if not (user_id := await get_user_id(db, user_name)):
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='Такого пользователя не существует.')
    if not (role_id := await find_role(db, role_title)):
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='Такой роли не существует.')
    return user_id, role_id[0].id


@app.post('/{role_title}/assign_to/{user_name}',
          summary='назначить роль пользователю',
          status_code=HTTPStatus.OK)
@admin_role_required
async def assign_role(user_name: str,
                      role_title: str,
                      request_header: str = Depends(header_scheme),
                      db: AsyncSession = Depends(get_session)):
    user_id, role_id = await check_login_role(user_name, role_title, db)
    print(await get_roles_by_id(db, user_id))
    if (role_id in set(await get_roles_by_id(db, user_id))):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Роль %s уже есть у пользователя %s.' % (role_title,
                                                            user_name)
        )

    await db.execute(insert(association_table).
                     values(user_id=user_id, role_id=role_id))
    await db.commit()
    return {
        'msg': 'Роль %s назначена пользователю %s.' % (role_title, user_name)
        }


@app.post('/{role_title}/revoke_from/{user_name}',
          summary='отобрать роль у пользователя',
          status_code=HTTPStatus.OK)
@admin_role_required
async def revoke_role(user_name: str,
                      role_title: str,
                      request_header: str = Depends(header_scheme),
                      db: AsyncSession = Depends(get_session)):
    user_id, role_id = await check_login_role(user_name, role_title, db)

    if not (role_id in set(await get_roles_by_id(db, user_id))):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Роли %s нет у пользователя %s.' % (role_title,
                                                       user_name)
        )

    await db.execute(delete(association_table).
                     where(user_id == user_id, role_id == role_id))
    await db.commit()
    return {
        'msg': 'Роль %s удалена у пользователя %s.' % (role_title, user_name)
        }


@app.get('/{user_name}',
         response_model=DBUserRole,
         summary='список всех ролей пользователя',
         status_code=HTTPStatus.OK)
@admin_role_required
async def get_user_roles(user_name: str,
                         request_header: str = Depends(header_scheme),
                         db: AsyncSession = Depends(get_session)):
    if not (await get_user_id(db, user_name)):
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='Такого пользователя не существует.')

    roles = await get_roles_by_login(db, user_name)
    return DBUserRole(login=user_name, roles=roles)
