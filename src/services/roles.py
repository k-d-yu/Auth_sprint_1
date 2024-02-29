from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


from models.role import Role, association_table
from models.user import User


async def find_role(db: AsyncSession,
                    role_title: str):
    role = await db.execute(select(Role.id).filter(Role.title == role_title))
    result = role.fetchone()
    return result[0] if result else None


async def get_roles(db: AsyncSession):
    roles = await db.execute(select(Role))
    return [row[0].title for row in roles.fetchall()]


async def get_user_id(db: AsyncSession,
                      login: str):
    user = await db.execute(select(User.id).filter(User.login == login))
    result = user.fetchone()
    return result[0] if result else None


async def get_user_login(db: AsyncSession,
                         id: str):
    user = await db.execute(select(User.login).filter(User.id == id))
    result = user.fetchone()
    return result[0] if result else None


async def get_roles_by_id(db: AsyncSession,
                          user_id: str):
    role_ids = await db.execute(
        select(association_table).
        filter(
            association_table.columns.user_id == user_id
        ))
    return [row[1] for row in role_ids.fetchall()]


async def get_roles_by_login(db: AsyncSession,
                             login: str):
    user_id = await get_user_id(db, login)
    roles_ids = await get_roles_by_id(db, user_id)

    roles = await db.execute(select(Role.title).filter(Role.id.in_(roles_ids)))

    return [row[0] for row in roles.fetchall()]
