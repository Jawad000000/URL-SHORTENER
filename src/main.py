from fastapi import FastAPI, status, Depends
from contextlib import asynccontextmanager
from src.urls.routes import url
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_session
from .urls.service import UrlService
from fastapi.responses import RedirectResponse
from src.auth.routes import auth_router
url_function = UrlService()



@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    print("server is stopping")


app = FastAPI(lifespan=lifespan)

app.include_router(url, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/{short_code}")
async def redirect_to_original_url(
    short_code: str,
    session: AsyncSession = Depends(get_session)
):

    original_url = await url_function.redirect_url(
        short_code,
        session
    )

    return RedirectResponse(
        url=original_url,
        status_code=status.HTTP_307_TEMPORARY_REDIRECT
    )