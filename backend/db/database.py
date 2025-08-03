"""
Database connection and session management.
"""

from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlmodel import SQLModel

from backend.core.config import settings


# Create async database engine
engine = create_async_engine(
    settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    echo=settings.database_echo,
    # 通过 connect_args 设置 schema
    # connect_args={"server_settings": {"search_path": "ore,public"}},
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session with dependency injection."""
    async with AsyncSession(engine) as session:
        yield session


# Annotated dependency for type hints
SessionDep = Annotated[AsyncSession, Depends(get_session)]
