"""
core/database.py — the async database connection.

SQLAlchemy 2.0 in **async** mode (via the asyncpg driver). Two things live here:

  • `engine`  — a shared pool of database connections for the whole app.
  • `get_db`  — a FastAPI dependency that hands each request its own session
                and guarantees it gets closed, even if the request errors.

Rookie note: a "session" is your conversation with the database for one unit of
work (one request). You never create sessions by hand in routes — you ask for
one with `db: AsyncSession = Depends(get_db)`.
"""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.config import settings

# One engine per process. `pool_pre_ping` quietly checks a connection is still
# alive before handing it out (avoids "server closed the connection" errors).
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,        # log SQL while DEBUG=true (handy when learning)
    pool_pre_ping=True,
)

# A factory that produces new AsyncSession objects bound to that engine.
# expire_on_commit=False keeps objects usable after commit (common in web apps).
AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency. Usage inside a route:

        @router.get("/example")
        async def example(db: AsyncSession = Depends(get_db)):
            ...

    The `async with` block opens a session and closes it automatically when the
    request finishes (success or failure).
    """
    async with AsyncSessionLocal() as session:
        yield session
