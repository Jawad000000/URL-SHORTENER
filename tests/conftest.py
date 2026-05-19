from collections.abc import AsyncGenerator
import sys
import types

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from src.config import Config
from src.db.database import get_session


redis_stub = types.ModuleType("src.db.redis")


async def token_in_blocklist_stub(jti: str) -> bool:
    return False


async def add_jti_to_blocklist_stub(jti: str) -> None:
    return None


redis_stub.token_in_blocklist = token_in_blocklist_stub
redis_stub.add_jti_to_blocklist = add_jti_to_blocklist_stub
sys.modules["src.db.redis"] = redis_stub

url_cache_stub = types.ModuleType("src.urls.cache")


async def get_cached_url_stub(short_code: str):
    return None


async def set_cached_url_stub(short_code: str, original_url: str) -> None:
    return None


async def delete_cached_url_stub(short_code: str) -> None:
    return None


url_cache_stub.get_cached_url = get_cached_url_stub
url_cache_stub.set_cached_url = set_cached_url_stub
url_cache_stub.delete_cached_url = delete_cached_url_stub
sys.modules["src.urls.cache"] = url_cache_stub

from src.main import app
from src.auth.models import User
from src.urls.models import Url


test_engine = create_async_engine(
    url=Config.TEST_DATABASE_URL,
    echo=False,
    poolclass=NullPool,
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def reset_test_database() -> AsyncGenerator[None, None]:
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

    yield


@pytest.fixture
def test_url_payload() -> dict[str, str]:
    return {"url": "https://example.com/articles/testing-fastapi"}


@pytest.fixture
def updated_url_payload() -> dict[str, str]:
    return {"url": "https://example.com/articles/updated-url"}


@pytest_asyncio.fixture
async def test_client() -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

    app.dependency_overrides.clear()
