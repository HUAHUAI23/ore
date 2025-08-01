"""
测试配置和fixture
"""

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from backend.main import app
from backend.db.database import get_session, engine
from backend.core.security import create_access_token
from backend.models.user import User


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def session() -> AsyncGenerator[AsyncSession, None]:
    """使用项目的数据库会话"""
    # 每个测试创建独立的会话，避免连接冲突
    async with AsyncSession(engine) as session:
        try:
            yield session
        finally:
            # 简单地关闭会话，让数据库连接池管理连接
            await session.close()


@pytest_asyncio.fixture
async def client(session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """创建测试客户端"""

    def get_test_session():
        return session

    app.dependency_overrides[get_session] = get_test_session

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://localhost:8000"
    ) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(session: AsyncSession) -> User:
    """创建或获取测试用户"""
    from backend.services.auth import AuthService
    from backend.schemas.user import UserCreateRequest
    from sqlmodel import select

    # 先尝试查找现有的测试用户
    statement = select(User).where(User.name == "testuser")
    result = await session.execute(statement)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        # 如果用户已存在，直接返回
        return existing_user

    # 如果用户不存在，创建新用户
    user_data = UserCreateRequest(
        name="testuser",
        nickname="Test User",
        email="test@example.com",
        password="StrongTest789!",
    )

    user = await AuthService.create_user(session, user_data)
    await session.flush()  # 使用flush而不是commit，保证事务回滚
    return user


@pytest_asyncio.fixture
async def auth_headers(test_user: User) -> dict:
    """创建认证头"""
    token_data = {
        "user_id": test_user.id,
        "name": test_user.name,
        "nickname": test_user.nickname,
        "email": test_user.email,
        "is_active": test_user.is_active,
    }

    access_token = create_access_token(
        subject=str(test_user.id), additional_claims=token_data
    )
    return {"Authorization": f"Bearer {access_token}"}
