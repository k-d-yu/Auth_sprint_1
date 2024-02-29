from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db.postgres import get_session
from models.user import User


async def get_user_id_by_login(login: str, db_session: AsyncSession) -> str:
    result = await db_session.execute(select(User.id).where(User.login == login))
    user = result.scalar_one_or_none()
    if user:
        return str(user)


async def main():
    async for session in get_session():
        user_id = await get_user_id_by_login("test_user", session)
        await session.close()

        if user_id:
            return user_id
