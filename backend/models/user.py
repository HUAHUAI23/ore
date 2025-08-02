"""
User database model - 带时区支持的现代化版本
DTO模型已移至 schemas/user.py
"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.orm import declared_attr
from sqlalchemy import Column, DateTime, func
from pydantic.alias_generators import to_snake

if TYPE_CHECKING:
    from .workflow import Workflow


class User(SQLModel, table=True):
    """用户模型 - 使用带时区的现代化版本"""
    
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return to_snake(cls.__name__)  # User -> user

    # 主键
    id: Optional[int] = Field(default=None, primary_key=True, description="用户ID")
    
    # 用户基本信息
    name: str = Field(max_length=100, unique=True, index=True, description="用户名")
    nickname: str = Field(max_length=50, description="用户昵称")
    
    # 联系信息
    email: Optional[str] = Field(
        default=None, max_length=255, unique=True, index=True, description="用户邮箱"
    )
    phone: Optional[str] = Field(
        default=None, max_length=20, unique=True, index=True, description="手机号码"
    )
    
    # 认证信息
    password_hash: str = Field(description="密码哈希值")
    
    # 状态信息
    is_active: bool = Field(default=True, description="是否激活")
    
    # 时间字段 - 使用带时区的现代化定义
    created_at: Optional[datetime] = Field(
        default=None,
        description="创建时间",
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),  # 数据库级别的默认值
        ),
    )
    
    updated_at: Optional[datetime] = Field(
        default=None,
        description="更新时间",
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),  # 自动更新时间戳
        ),
    )
    
    last_login: Optional[datetime] = Field(
        default=None,
        description="最后登录时间",
        sa_column=Column(DateTime(timezone=True)),
    )
    
    # 关系定义
    workflows: list["Workflow"] = Relationship(back_populates="created_by_user")
    
    class Config:
        """Pydantic配置"""
        # 确保时间字段的JSON序列化格式一致
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }