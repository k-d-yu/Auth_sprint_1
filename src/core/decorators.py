from functools import wraps
from typing import Callable
from http import HTTPStatus
from fastapi import HTTPException

from jose import jwt
from jose.exceptions import JWTError
from jose.jwt import ExpiredSignatureError

from core.config import ADMIN_ROLES, jwt_settings
from services.roles import get_user_login, get_roles_by_login


def admin_role_required(fn: Callable) -> Callable:
    @wraps(fn)
    async def wrapper(*args, **kwargs):
        if not (auth_token := kwargs['request_header']):
            raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                                detail='Аваторизация не пройдена.')
        try:
            user = jwt.decode(auth_token, jwt_settings.jwt_secret_key,
                              algorithms=[jwt_settings.jwt_algorithm])
        except ExpiredSignatureError:
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN,
                                detail='Токен истек.')
        except JWTError:
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN,
                                detail='Некорректный токен.')
        login = await get_user_login(kwargs['db'], user['id'])
        user_roles = await get_roles_by_login(kwargs['db'], login)
        if not (set(ADMIN_ROLES) == set(user_roles)):
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN,
                                detail='Недостаточно прав.')
        return await fn(*args, **kwargs)
    return wrapper
