"""
User database model - 只包含数据库模型定义
DTO模型已移至 schemas/user.py
"""

from datetime import datetime, timezone

from pydantic import EmailStr
from sqlalchemy import func
from sqlmodel import Column, DateTime, Field, SQLModel, Text
from sqlalchemy.orm import declared_attr
from pydantic.alias_generators import to_snake


class User(SQLModel, table=True):
    """User database table model."""

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return to_snake(cls.__name__)  # User -> user

    id: int | None = Field(default=None, primary_key=True, description="用户ID")
    name: str = Field(max_length=100, unique=True, index=True, description="用户名")
    nickname: str = Field(max_length=50, description="用户昵称")
    email: EmailStr | None = Field(
        default=None, unique=True, index=True, description="用户邮箱"
    )
    phone: str | None = Field(
        default=None, max_length=20, unique=True, index=True, description="手机号码"
    )
    password_hash: str = Field(sa_column=Column(Text), description="密码哈希值")
    is_active: bool = Field(default=True, description="是否激活")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
        description="创建时间",
    )
    last_login: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="最后登录时间",
    )
