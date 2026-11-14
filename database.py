from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from config import settings

# the "." is the current dir
# blog.db gets created automatically
# the "+" tells sqlalchemy which async driver to use for sqlite database
# SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./blog.db"

# engine = create_async_engine(
#     SQLALCHEMY_DATABASE_URL,
#     connect_args={"check_same_thread": False}, # sqlite requires only 1 thread
# )

engine = create_async_engine(settings.database_url)

# Standard fastapi setup
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False, # Recommended for async bc prevents issues with expired objects after commit (avoids lazy loading)
)

# Allows modern type checkers
class Base(DeclarativeBase):
    pass

# dependency function that provides sessions to the routes
# fastapi uses dependency injection for each request and does a clean up automatically likes a file
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session