from .models import User
from .schemas import UserAccount
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from .utils import verify_password, generate_password_hash


class User_service:
    async def get_user(self, email: str, session: AsyncSession):
        statement = select(User).where(User.email == email)

        result = await session.execute(statement)
        user = result.scalar_one_or_none()

        return user

    async def get_user_by_id(self, user_id: int, session: AsyncSession):
        statement = select(User).where(User.id == user_id)

        result = await session.execute(statement)
        user = result.scalar_one_or_none()

        return user

    async def user_exists(self, email: str, session: AsyncSession):
        user = await self.get_user(email, session)

        return True if user is not None else False

    async def create_user(self, user_data: UserAccount, session: AsyncSession):
        user_data_dict = user_data.model_dump()
        new_user = User(**user_data_dict)
        new_user.password_hash = generate_password_hash(user_data_dict["password"])
        session.add(new_user)
        await session.commit()

        return new_user
