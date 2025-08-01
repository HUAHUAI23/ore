"""
Authentication service for user login and registration.
现代化SQLModel版本 - 使用最佳实践
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, and_
from sqlmodel import select
from sqlalchemy.exc import IntegrityError

from backend.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
)
from backend.models.user import User
from backend.schemas.user import UserCreateRequest
from backend.schemas.auth import UserLoginRequest
from backend.utils.logger import get_logger

from enum import Enum


class ConflictType(str, Enum):
    NAME = "name"
    EMAIL = "email"
    UNKNOWN = "unknown"
    NONE = "none"


logger = get_logger(__name__)


class AuthService:
    """Authentication service for handling user operations."""

    # ============================================
    # 基础查询方法 - 现代化查询
    # ============================================

    @staticmethod
    async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
        """Get user by email - 优化版本"""
        statement = select(User).where(
            (User.email == email) & (User.is_active == True)  # 只查询活跃用户
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_name(session: AsyncSession, name: str) -> Optional[User]:
        """Get user by name - 优化版本"""
        statement = select(User).where(
            (User.name == name) & (User.is_active == True)  # 只查询活跃用户
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID - 移到前面，逻辑更清晰"""
        statement = select(User).where(User.id == user_id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    @staticmethod
    async def check_user_exists(
        session: AsyncSession, name: Optional[str] = None, email: Optional[str] = None
    ) -> tuple[bool, ConflictType]:
        """使用 Enum 确保类型安全"""
        conditions = []

        if name:
            conditions.append(User.name == name)
        if email:
            conditions.append(User.email == email)

        if not conditions:
            return False, ConflictType.NONE

        statement = select(User.name, User.email).where(or_(*conditions))
        result = await session.execute(statement)
        existing_user = result.first()

        if not existing_user:
            return False, ConflictType.NONE

        if name and existing_user.name == name:
            return True, ConflictType.NAME
        if email and existing_user.email == email:
            return True, ConflictType.EMAIL

        return True, ConflictType.UNKNOWN

    # ============================================
    # 用户创建 - 现代化错误处理
    # ============================================

    @staticmethod
    async def create_user(
        session: AsyncSession, user_create: UserCreateRequest
    ) -> User:
        """Create a new user - 现代化版本"""

        # 预检查用户是否存在
        exists, conflict_field = await AuthService.check_user_exists(
            session, name=user_create.name, email=user_create.email
        )

        if exists:
            error_messages = {
                ConflictType.NAME: "用户名已存在",
                ConflictType.EMAIL: "邮箱已存在",
                ConflictType.UNKNOWN: "用户信息冲突",
                ConflictType.NONE: "用户已存在",
            }
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_messages[conflict_field],
            )

        # 使用UTC时间
        password_hash = get_password_hash(user_create.password)

        # 创建用户实例
        db_user = User(
            name=user_create.name,
            nickname=user_create.nickname or user_create.name,
            email=user_create.email,
            phone=user_create.phone,
            is_active=True,
            password_hash=password_hash,
            # created_at 会自动设置为 func.now()
        )

        try:
            session.add(db_user)
            await session.commit()
            await session.refresh(db_user)

            logger.info(f"Created new user: {user_create.name} (ID: {db_user.id})")
            return db_user

        except IntegrityError as e:
            await session.rollback()
            logger.error(
                f"Database integrity error creating user {user_create.name}: {e}"
            )

            # 解析具体的约束错误
            error_str = str(e)
            if "name" in error_str:
                detail = "用户名已存在"
            elif "email" in error_str:
                detail = "邮箱已存在"
            elif "phone" in error_str:
                detail = "手机号已存在"
            else:
                detail = "用户信息冲突，请检查用户名、邮箱或手机号"

            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
        except Exception as e:
            await session.rollback()
            logger.error(f"Unexpected error creating user {user_create.name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="创建用户失败"
            )

    # ============================================
    # 认证相关 - 现代化安全实践
    # ============================================

    @staticmethod
    async def authenticate_user(
        session: AsyncSession, identifier: str, password: str, login_by: str = "name"
    ) -> Optional[User]:
        """
        Authenticate user - 支持多种登录方式

        Args:
            identifier: 用户标识符（用户名、邮箱等）
            password: 密码
            login_by: 登录方式 ("name", "email", "auto")
        """

        # 根据登录方式获取用户
        if login_by == "name":
            user = await AuthService.get_user_by_name(session, identifier)
        elif login_by == "email":
            user = await AuthService.get_user_by_email(session, identifier)
        elif login_by == "auto":
            # 自动识别：包含@符号则认为是邮箱
            if "@" in identifier:
                user = await AuthService.get_user_by_email(session, identifier)
            else:
                user = await AuthService.get_user_by_name(session, identifier)
        else:
            logger.warning(f"Invalid login_by parameter: {login_by}")
            return None

        if not user:
            logger.warning(f"Authentication failed: user not found for {identifier}")
            return None

        if not user.is_active:
            logger.warning(f"Authentication failed: user inactive for {identifier}")
            return None

        if not verify_password(password, user.password_hash):
            logger.warning(f"Authentication failed: invalid password for {identifier}")
            return None

        logger.info(f"User authenticated successfully: {identifier} (ID: {user.id})")
        return user

    @staticmethod
    async def update_last_login(session: AsyncSession, user: User) -> User:
        """Update user's last login timestamp - 返回更新后的用户"""
        # 使用UTC时间
        user.last_login = datetime.now(timezone.utc)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    # ============================================
    # Token生成 - 提取为独立方法
    # ============================================

    @staticmethod
    def create_user_token(user: User) -> str:
        """Create access token for user - 独立的token创建方法"""
        if user.id is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="用户ID缺失"
            )

        # 在token中包含用户基本信息
        user_claims = {
            "user_id": user.id,
            "name": user.name,
            "nickname": user.nickname,
            "email": user.email,
            "phone": user.phone,
            "is_active": user.is_active,
            "last_login": user.last_login.isoformat() if user.last_login else None,
        }

        return create_access_token(
            subject=str(user.id), additional_claims=user_claims  # 转换为字符串，更安全
        )

    # ============================================
    # 高级业务方法 - 现代化实现
    # ============================================

    @staticmethod
    async def login_user(
        session: AsyncSession, login_data: UserLoginRequest
    ) -> tuple[User, str]:
        """
        Login user - 现代化版本

        Returns:
            Tuple of (user, access_token)
        """
        try:
            # 认证用户 - 支持自动识别登录方式
            user = await AuthService.authenticate_user(
                session,
                login_data.name,
                login_data.password,
                login_by="auto",  # 自动识别用户名或邮箱
            )

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="用户名或密码错误",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # 更新最后登录时间
            user = await AuthService.update_last_login(session, user)

            # 生成访问令牌
            access_token = AuthService.create_user_token(user)

            logger.info(f"User logged in: {login_data.name} (ID: {user.id})")
            return user, access_token

        except HTTPException:
            # 重新抛出HTTP异常
            raise
        except Exception as e:
            logger.error(f"Unexpected error during login for {login_data.name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="登录失败"
            )

    @staticmethod
    async def register_user(
        session: AsyncSession, user_create: UserCreateRequest
    ) -> tuple[User, str]:
        """
        Register a new user - 现代化版本

        Returns:
            Tuple of (user, access_token)
        """
        try:
            # 创建用户（内部已包含重复检查）
            user = await AuthService.create_user(session, user_create)

            # 设置最后登录时间（新用户注册即登录）
            user = await AuthService.update_last_login(session, user)

            # 生成访问令牌
            access_token = AuthService.create_user_token(user)

            logger.info(
                f"New user registered and logged in: {user_create.name} (ID: {user.id})"
            )
            return user, access_token

        except HTTPException:
            # 重新抛出HTTP异常（来自create_user）
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error during registration for {user_create.name}: {e}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="注册失败"
            )

    # ============================================
    # 用户管理 - 新增实用方法
    # ============================================

    @staticmethod
    async def deactivate_user(session: AsyncSession, user_id: int) -> bool:
        """停用用户账户"""
        user = await AuthService.get_user_by_id(session, user_id)
        if not user:
            return False

        user.is_active = False
        session.add(user)
        await session.commit()

        logger.info(f"User deactivated: {user.name} (ID: {user_id})")
        return True

    @staticmethod
    async def activate_user(session: AsyncSession, user_id: int) -> bool:
        """激活用户账户"""
        user = await AuthService.get_user_by_id(session, user_id)
        if not user:
            return False

        user.is_active = True
        session.add(user)
        await session.commit()

        logger.info(f"User activated: {user.name} (ID: {user_id})")
        return True

    @staticmethod
    async def change_password(
        session: AsyncSession, user_id: int, old_password: str, new_password: str
    ) -> bool:
        """更改用户密码"""
        user = await AuthService.get_user_by_id(session, user_id)
        if not user:
            return False

        # 验证旧密码
        if not verify_password(old_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="原密码错误"
            )

        # 设置新密码
        user.password_hash = get_password_hash(new_password)
        session.add(user)
        await session.commit()

        logger.info(f"Password changed for user: {user.name} (ID: {user_id})")
        return True

    @staticmethod
    async def get_user_stats(session: AsyncSession, user_id: int) -> Optional[dict]:
        """获取用户统计信息"""
        user = await AuthService.get_user_by_id(session, user_id)
        if not user:
            return None

        # 可以添加更多统计信息，比如工作流数量等
        return {
            "user_id": user.id,
            "name": user.name,
            "email": user.email,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "last_login": user.last_login,
            "has_email": bool(user.email),
            "has_phone": bool(user.phone),
        }
