from fastapi import APIRouter, HTTPException, Depends, Request, Query
from http import HTTPStatus
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from werkzeug.security import generate_password_hash

from db.postgres import get_session
from models.user import User
from models.session import Session
from schemas.user import UserCreate, UserInDB, ChangePassword, UserLogin
from services.user import (create_access_token, create_refresh_token, get_existing_refresh_token,
                           get_existing_access_token, get_refresh_token_from_id, del_access_token,
                           del_refresh_token)

app = APIRouter()


@app.post('/register/', response_model=UserInDB, summary='Регистрация пользователей.',
          description='Регистрация пользователей.')
async def register_user(user_data: UserCreate,
                        db: AsyncSession = Depends(get_session)
                        ):
    new_user = User(login=user_data.login,
                    password=user_data.password,
                    first_name=user_data.first_name,
                    last_name=user_data.last_name)
    db.add(new_user)
    try:
        await db.commit()
    except IntegrityError:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Такой логин существует.')
    return UserInDB(**new_user.__dict__)


@app.post('/login/', summary='Вход пользователя.', description='Вход пользователя и получение токенов.')
async def login_user(user_login: UserLogin,
                     request: Request,
                     db: AsyncSession = Depends(get_session)
                     ):
    user_agent = request.headers.get('User-Agent', 'Unknown')
    result = await db.execute(select(User).filter(User.login == user_login.login))
    user_row = result.fetchone()

    if not user_row:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Пользователь с указанным логином не найден.')

    user = user_row[0]

    if not user.check_password(user_login.password):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Неверный пароль.')

    existing_refresh_token = await get_existing_refresh_token(str(user.id))
    existing_access_token = await get_existing_access_token(str(user.id))

    if existing_refresh_token and existing_access_token:
        session = Session(user_id=user.id, user_agent=user_agent)
        db.add(session)
        await db.commit()
        return {'id': user.id, "access_token": existing_access_token, "refresh_token": existing_refresh_token}

    if existing_refresh_token:
        session = Session(user_id=user.id, user_agent=user_agent)
        db.add(session)
        await db.commit()
        access_token = await create_access_token({'id': str(user.id)})
        return {'id': user.id, "access_token": access_token, "refresh_token": existing_refresh_token}

    access_token = await create_access_token({'id': str(user.id)})
    refresh_token = await create_refresh_token(str(user.id))

    session = Session(user_id=user.id, user_agent=user_agent)
    db.add(session)
    await db.commit()

    return {'id': user.id, "access_token": access_token, "refresh_token": refresh_token}


@app.get('/refresh-token/', summary='Обновление access-токена.',
         description='Обновление access-токена по refresh-токену.')
async def refresh_token(user_id: str,
                        db: AsyncSession = Depends(get_session),
                        ):
    refresh_token = await get_refresh_token_from_id(user_id)

    if not refresh_token:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail='Refresh-токен отсутствует для данного пользователя.')

    result = await db.execute(select(User.login).filter(User.id == user_id))
    login = result.fetchone()[0]
    access_token = await create_access_token({'id': str(user_id)})
    return {'login': login, 'id': user_id, 'access_token': access_token}


@app.get('/logout/', summary='Выход пользователя.', description='Выход пользователя из аккаунта.')
async def logout_user(user_id: str):
    existing_access_token = await get_existing_access_token(user_id)
    existing_refresh_token = await get_existing_refresh_token(user_id)

    if existing_access_token:
        await del_access_token(user_id)

    if existing_refresh_token:
        await del_refresh_token(user_id)

    if not existing_access_token and not existing_refresh_token:
        return {'message': 'Необходимо сначала войти в аккаунт.'}

    return {'message': 'Пользователь успешно вышел из аккаунта.'}


@app.post('/change-password/', summary='Изменение пароля пользователя.',
          description='Изменение пароля пользователя.')
async def change_password(user_id: str,
                          password_data: ChangePassword,
                          db: AsyncSession = Depends(get_session)):
    user = await db.get(User, user_id)

    if not user:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Пользователь не найден.')

    if not user.check_password(password_data.current_password):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='Текущий пароль введен неверно.')

    user.password = generate_password_hash(password_data.new_password)
    await db.commit()
    return {'message': 'Пароль успешно изменен'}


@app.get('/sessions/', summary='История входов пользователя.',
         description='Получение истории входов в аккаунт пользователя.')
async def get_user_sessions(user_id: str,
                            page: int = Query(default=1, ge=1),
                            page_size: int = Query(default=10, ge=1),
                            db: AsyncSession = Depends(get_session)
                            ):
    total_sessions = await db.execute(select(func.count(Session.id)).filter(Session.user_id == user_id))
    total_sessions_count = total_sessions.scalar()

    total_pages = (total_sessions_count + page_size - 1) // page_size
    offset = (page - 1) * page_size

    user_sessions = await db.execute(
        select(Session)
        .filter(Session.user_id == user_id)
        .offset(offset)
        .limit(page_size)
    )
    sessions = user_sessions.scalars().all()

    if not sessions:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='История входов не найдена.')

    next_page = page + 1 if page < total_pages else None
    previous_page = page - 1 if page > 1 else None

    return {
        'sessions': sessions,
        'page': page,
        'page_size': page_size,
        'total_pages': total_pages,
        'next_page': next_page,
        'previous_page': previous_page
    }
