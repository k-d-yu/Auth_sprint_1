import os

from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv


DOTENV = os.path.join(os.path.dirname(__file__), "../../.env")

load_dotenv(dotenv_path=DOTENV,
            verbose=True,
            override=True)


class Settings(BaseSettings):
    redis_host: str = Field(default='localhost')
    redis_port: int = Field(default=6379)
    project_name: str = 'AUTH API'
    db_host: str = Field(default='localhost')
    db_port: int = Field(default=5432)
    db_name: str = Field(default='users_db')
    postgres_user: str = Field(default='postgres')
    postgres_password: str = Field(default='postgres')

    cache_lifetime: int = Field(default=60 * 5, env='CACHE_EXPIRE_IN_SECONDS')

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


class SuperuserSettings(BaseSettings, extra='allow'):

    login: str = Field(default='admin')
    password: str = Field(default='password')

    api_host: str = Field('localhost', env='API_HOST')
    api_port: int = Field(default=80)

    class Config:
        env_file = DOTENV
        env_file_encoding = 'utf-8'


class JWTSettings(BaseSettings):
    jwt_secret_key: str = Field(default='123')
    jwt_algorithm: str = Field(default='HS256')
    access_token_expire_minutes: int = Field(default=5)
    refresh_token_expire_days: int = Field(default=2)


settings = Settings()
jwt_settings = JWTSettings()
superuser_settings = SuperuserSettings()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

API_URL = f'http://{superuser_settings.api_host}:{superuser_settings.api_port}/api/'

ADMIN_ROLES = ['administrator', 'subscriber', 'user']
