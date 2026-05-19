# routes.py
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_session
from fastapi import APIRouter, status, Depends
from .service import UrlService
from src.urls.schemas import (
    ShortURLRequest,
    ShortURLResponse,
    URLStatsResponse,
)
from fastapi.responses import RedirectResponse
from src.auth.dependencies import  get_current_user
from src.rate_limiter import rate_limit



url = APIRouter()
url_function = UrlService()


@url.post(
    "/shorten", response_model=ShortURLResponse, status_code=status.HTTP_201_CREATED
)
async def create_url(
    new_url: ShortURLRequest,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user),
    _: None = Depends(rate_limit),
):

    created_url = await url_function.create_url(new_url, current_user, session)

    return created_url


@url.get(
    "/shorten/{short_code}",
    response_model=ShortURLResponse,
    status_code=status.HTTP_200_OK,
)
async def get_url(
    short_code: str,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user),
):

    found_url = await url_function.get_url(short_code,current_user, session)

    return found_url


@url.patch(
    "/shorten/{short_code}",
    response_model=ShortURLResponse,
    status_code=status.HTTP_200_OK,
)
async def update_url(
    short_code: str,
    updated_url: ShortURLRequest,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user),
):

    updated_data = await url_function.update_url(short_code, updated_url, current_user, session)

    return updated_data


@url.delete("/shorten/{short_code}", status_code=status.HTTP_200_OK,)
async def delete_url(
    short_code: str,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user),
):

    await url_function.delete_url(short_code, current_user, session)


@url.get(
    "/shorten/{short_code}/stats",
    response_model=URLStatsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_url_stats(
    short_code: str,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user),
):

    stats = await url_function.get_stats(short_code,current_user, session)

    return stats
