from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from datetime import datetime, timezone

from .security import decode_token, TokenType
from ..models.user import User

security = HTTPBearer()


def create_user_from_token_claims(payload: dict) -> User:
    """
    从token的payload构建User对象，避免数据库查询
    """
    try:
        # 解析last_login时间戳
        last_login = None
        if payload.get("last_login"):
            last_login = datetime.fromisoformat(payload["last_login"])

        # 构建User对象
        user = User(
            id=payload["user_id"],
            name=payload["name"],
            nickname=payload["nickname"],
            email=payload.get("email"),  # 可能为None
            phone=payload.get("phone"),  # 可能为None
            is_active=payload["is_active"],
            password_hash="",  # token中不包含密码哈希
            last_login=last_login,
            created_at=datetime.now(timezone.utc),  # 使用timezone-aware时间
        )
        return user
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: missing {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """
    优化版本：从JWT token直接构建用户对象，避免数据库查询
    """
    token = credentials.credentials
    payload = decode_token(token, TokenType.ACCESS)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 检查token中是否包含完整的用户信息
    if "user_id" in payload and "email" in payload and "name" in payload:
        # 使用token中的用户信息，无需数据库查询（性能优化）
        user = create_user_from_token_claims(payload)

        # 验证用户状态
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    else:
        # 如果token中没有完整用户信息，返回错误
        # 这要求客户端重新登录获取新的token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token format outdated, please login again",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
) -> Optional[dict]:
    """
    Dependency to optionally get current user from JWT token
    """
    if not credentials:
        return None

    token = credentials.credentials
    payload = decode_token(token, TokenType.ACCESS)

    if payload is None:
        return None

    user_id = payload.get("sub")
    if user_id is None:
        return None

    return {"user_id": user_id, "payload": payload}
