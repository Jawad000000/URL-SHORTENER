from sqlmodel import select
from .models import Url
from .schemas import (
    ShortURLRequest,
    ShortURLResponse,
    URLStatsResponse,
)
from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi import status
from fastapi.exceptions import HTTPException
from .utils import generate_short_code
from src.config import Config
from .cache import get_cached_url, set_cached_url, delete_cached_url

BASE_URL = Config.BASE_URL


class UrlService:

    def _to_response(self, url: Url) -> ShortURLResponse:

        return ShortURLResponse(
            url=url.original_url,
            short_code=url.short_code,
            short_url=f"{BASE_URL}/{url.short_code}",
            created_at=url.created_at,
            updated_at=url.updated_at,
        )

    def _to_stats_response(self, url: Url) -> URLStatsResponse:

        return URLStatsResponse(
            url=url.original_url,
            short_code=url.short_code,
            short_url=f"{BASE_URL}/{url.short_code}",
            created_at=url.created_at,
            updated_at=url.updated_at,
            access_count=url.access_count,
        )

    async def find_by_short_code(self, input_code: str, session: AsyncSession):

        statement = select(Url).where(Url.short_code == input_code)

        result = await session.execute(statement)

        return result.scalar_one_or_none()

    async def create_url(self, input_url: ShortURLRequest, current_user, session: AsyncSession):
        max_attempts = 5

        for _ in range(max_attempts):

            new_code = generate_short_code()

            existing_code = await self.find_by_short_code(new_code, session)

            if existing_code is None:
                new_url = Url(
                original_url=str(input_url.url),
                short_code=new_code,
                user_id=current_user.id)
                
                session.add(new_url)

                await session.commit()

                await session.refresh(new_url)

                return self._to_response(new_url)
    
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Failed to generate unique short code")

    async def get_user_url_model(self, input_code: str,current_user, session: AsyncSession):

        statement = select(Url).where(
            Url.short_code == input_code,
            Url.user_id == current_user.id,
        )
        result = await session.execute(statement)
        url = result.scalar_one_or_none()
        if url is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="URL not found"
            )

        return url
    
    async def get_url_model(self, input_code: str, session: AsyncSession):
        url = await self.find_by_short_code(input_code, session)

        if url is None:
            raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="URL not found",)

        return url

    async def get_url(self, input_code: str,current_user, session: AsyncSession):

        url = await self.get_user_url_model(input_code, current_user, session)

        return self._to_response(url)

    async def update_url(
        self, input_code: str, updated_url: ShortURLRequest, current_user, session: AsyncSession
    ):

        url_to_update = await self.get_user_url_model(input_code, current_user,session)

        url_to_update.original_url = str(updated_url.url)

        session.add(url_to_update)

        await session.commit()

        await delete_cached_url(input_code)

        await session.refresh(url_to_update)

        return self._to_response(url_to_update)

    async def delete_url(self, input_code: str,current_user, session: AsyncSession):

        url_to_delete = await self.get_user_url_model(input_code,current_user, session)

        await session.delete(url_to_delete)

        await session.commit()
        await delete_cached_url(input_code)

    async def get_stats(self, input_code: str, current_user, session: AsyncSession):

        stat_url = await self.get_user_url_model(input_code,current_user, session)

        return self._to_stats_response(stat_url)

    async def redirect_url(self, input_code: str, session: AsyncSession):

        cached_url = await get_cached_url(input_code)

        if cached_url:
            return cached_url
        
        url = await self.get_url_model(input_code, session)

        url.access_count += 1

        session.add(url)

        await session.commit()

        await session.refresh(url)
        await set_cached_url(input_code, url.original_url)

        return url.original_url
