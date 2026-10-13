"""Worked example: a single real Postgres per session via Testcontainers (PY-10)."""
from collections.abc import AsyncIterator, Iterator

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from testcontainers.postgres import PostgresContainer

from mypkg.data.migrate import run_migrations


@pytest.fixture(scope="session")
def pg_url() -> Iterator[str]:
    with PostgresContainer("postgres:17-alpine", driver="asyncpg") as pg:  # same major as production
        url = pg.get_connection_url()
        run_migrations(url)
        yield url


@pytest.fixture
async def engine(pg_url: str) -> AsyncIterator[AsyncEngine]:
    eng = create_async_engine(pg_url)
    yield eng
    await eng.dispose()
