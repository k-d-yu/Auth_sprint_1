from api.user import app as users_app
from fastapi import FastAPI
from api.v1.roles import app as roles_app
from fastapi import APIRouter

from core.config import settings

router = APIRouter()
router.include_router(users_app, prefix='/users', tags=['users'])
router.include_router(roles_app, prefix='/roles', tags=['roles'])

app = FastAPI(
    title=settings.project_name,
    docs_url='/api',
    openapi_url='/api/openapi.json'
)

app.include_router(router, prefix='/api')