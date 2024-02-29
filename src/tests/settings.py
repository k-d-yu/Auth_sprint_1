from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    api_host: str = 'localhost'
    api_port: str = '80'


settings = Settings()

API_USERS = f'http://{settings.api_host}:{settings.api_port}/api/users/'

API_ROLES = f'http://{settings.api_host}:{settings.api_port}/api/roles'
