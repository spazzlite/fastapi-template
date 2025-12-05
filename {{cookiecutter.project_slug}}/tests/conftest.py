import asyncio

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from src.main import app

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@postgres:5432/test_db"


@pytest.fixture(scope="session")
def alembic_cfg() -> Config:
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
    return cfg


@pytest.fixture(scope="session", autouse=True)
def apply_migrations(alembic_cfg: Config):
    command.upgrade(alembic_cfg, "head")
    yield


@pytest_asyncio.fixture
async def async_engine(apply_migrations):  # зависим от миграций
    engine = create_async_engine(DATABASE_URL, echo=True, future=True)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def async_session(async_engine):
    async with async_engine.connect() as conn:
        outer = await conn.begin()
        session = AsyncSession(bind=conn, expire_on_commit=False)
        await session.begin_nested()

        @event.listens_for(session.sync_session, "after_transaction_end")
        def _restart_savepoint(sess, trans):
            if trans.nested and not trans._parent.nested:

                async def _reopen():
                    await session.begin_nested()

                asyncio.get_running_loop().create_task(_reopen())

        try:
            yield session
        finally:
            await session.close()
            if outer.is_active:
                await outer.rollback()


@pytest.fixture(scope="session")
def test_client():
    with TestClient(app) as client:
        yield client
