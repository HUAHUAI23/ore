"""
Authentication service for user login and registration.
"""

from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from backend.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
)
from backend.models.user import User
from backend.schemas.user import UserCreateRequest
from backend.schemas.auth import UserLoginRequest
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class AuthService:
    """Authentication service for handling user operations."""

    @staticmethod
    async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
        """Get user by email."""
        statement = select(User).where(User.email == email)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_name(session: AsyncSession, name: str) -> Optional[User]:
        """Get user by name."""
        statement = select(User).where(User.name == name)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(
        session: AsyncSession, user_create: UserCreateRequest
    ) -> User:
        """Create a new user."""
        # Hash the password
        password_hash = get_password_hash(user_create.password)

        # Create user instance
        db_user = User(
            name=user_create.name,
            nickname=user_create.nickname
            or user_create.name,  # 如果没有昵称，使用用户名
            email=user_create.email,
            phone=user_create.phone,
            is_active=True,  # 新用户默认激活
            password_hash=password_hash,
        )

        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)

        logger.info(f"Created new user: {user_create.name}")
        return db_user

    @staticmethod
    async def authenticate_user(
        session: AsyncSession, name: str, password: str
    ) -> Optional[User]:
        """Authenticate user with username and password."""
        user = await AuthService.get_user_by_name(session, name)

        if not user:
            logger.warning(f"Authentication failed: user not found for name {name}")
            return None

        if not user.is_active:
            logger.warning(f"Authentication failed: user inactive for name {name}")
            return None

        if not verify_password(password, user.password_hash):
            logger.warning(f"Authentication failed: invalid password for name {name}")
            return None

        logger.info(f"User authenticated successfully: {name}")
        return user

    @staticmethod
    async def update_last_login(session: AsyncSession, user: User) -> None:
        """Update user's last login timestamp."""
        user.last_login = datetime.utcnow()
        session.add(user)
        await session.commit()
        await session.refresh(user)

    @staticmethod
    async def login_user(
        session: AsyncSession, login_data: UserLoginRequest
    ) -> tuple[User, str]:
        """
        Login user with username and password.

        Returns:
            Tuple of (user, access_token)
        """
        # Try to authenticate existing user
        user = await AuthService.authenticate_user(
            session, login_data.name, login_data.password
        )

        if not user:
            logger.warning(f"Login failed: invalid credentials for {login_data.name}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Update last login
        await AuthService.update_last_login(session, user)

        # Generate access token with user info
        if user.id is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User ID is missing",
            )

        # 在token中包含用户基本信息，避免数据库查询
        user_claims = {
            "user_id": user.id,
            "email": user.email,
            "name": user.name,
            "nickname": user.nickname,
            "phone": user.phone,
            "is_active": user.is_active,
            "last_login": user.last_login.isoformat() if user.last_login else None,
        }
        access_token = create_access_token(
            subject=user.id, additional_claims=user_claims
        )

        logger.info(f"User logged in: {login_data.name}")
        return user, access_token

    @staticmethod
    async def register_user(
        session: AsyncSession, user_create: UserCreateRequest
    ) -> tuple[User, str]:
        """
        Register a new user.

        Returns:
            Tuple of (user, access_token)
        """
        # Check if username already exists
        existing_user = await AuthService.get_user_by_name(session, user_create.name)
        if existing_user:
            logger.warning(
                f"Registration failed: username already exists {user_create.name}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )

        # Check if email already exists (if provided)
        if user_create.email:
            existing_email_user = await AuthService.get_user_by_email(
                session, user_create.email
            )
            if existing_email_user:
                logger.warning(
                    f"Registration failed: email already exists {user_create.email}"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists",
                )

        try:
            user = await AuthService.create_user(session, user_create)

            # Update last login for new user
            await AuthService.update_last_login(session, user)

            # Generate access token with user info
            if user.id is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="User ID is missing",
                )

            # 在token中包含用户基本信息，避免数据库查询
            user_claims = {
                "user_id": user.id,
                "email": user.email,
                "name": user.name,
                "nickname": user.nickname,
                "phone": user.phone,
                "is_active": user.is_active,
                "last_login": user.last_login.isoformat() if user.last_login else None,
            }
            access_token = create_access_token(
                subject=user.id, additional_claims=user_claims
            )

            logger.info(f"New user registered: {user_create.name}")
            return user, access_token

        except Exception as e:
            logger.error(f"Failed to register user {user_create.name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user account",
            )

    @staticmethod
    async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID."""
        statement = select(User).where(User.id == user_id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()
