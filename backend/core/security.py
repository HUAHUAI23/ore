"""
纯现代化的安全模块 - 直接使用 argon2-cffi，无需 passlib
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional, Literal
from jose import jwt, JWTError, ExpiredSignatureError
import argon2
import secrets
import logging
import re
from enum import Enum

from .config import settings

logger = logging.getLogger(__name__)


class TokenType(str, Enum):
    """JWT Token 类型枚举"""
    ACCESS = "access"
    REFRESH = "refresh"

# 直接使用 argon2-cffi 创建密码哈希器
# 这是最现代、最安全的密码哈希方式
password_hasher = argon2.PasswordHasher(
    time_cost=3,        # 时间代价（迭代次数）
    memory_cost=65536,  # 内存代价（64MB）
    parallelism=1,      # 并行度
    hash_len=32,        # 哈希长度
    salt_len=16,        # 盐长度
)

def create_access_token(
    subject: Union[str, int], 
    expires_delta: Optional[timedelta] = None,
    token_type: TokenType = TokenType.ACCESS,
    additional_claims: Optional[dict] = None
) -> str:
    """
    创建 JWT 令牌
    
    Args:
        subject: 令牌主体（通常是用户ID）
        expires_delta: 过期时间增量
        token_type: 令牌类型
        additional_claims: 额外的声明
    
    Returns:
        编码后的 JWT 令牌
    """
    now = datetime.now(timezone.utc)
    
    if expires_delta:
        expire = now + expires_delta
    else:
        # 根据 token 类型设置不同的过期时间
        if token_type == TokenType.REFRESH:
            expire = now + timedelta(days=7)  # 刷新令牌 7 天
        else:
            expire = now + timedelta(minutes=settings.access_token_expire_minutes)
    
    # 基础载荷
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "iat": now,  # 签发时间
        "jti": secrets.token_urlsafe(16),   # JWT ID，防止重放攻击
        "type": token_type.value,  # 令牌类型
    }
    
    # 添加额外声明
    if additional_claims:
        to_encode.update(additional_claims)
    
    try:
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.secret_key, 
            algorithm=settings.algorithm
        )
        logger.debug(f"Created {token_type.value} token for subject: {subject}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Failed to create {token_type.value} token: {e}")
        raise

def create_refresh_token(subject: Union[str, int]) -> str:
    """
    创建刷新令牌（有效期更长）
    """
    return create_access_token(
        subject=subject,
        token_type=TokenType.REFRESH
    )

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    使用 Argon2 验证密码
    
    Args:
        plain_password: 明文密码
        hashed_password: Argon2 哈希后的密码
    
    Returns:
        验证结果
    """
    try:
        password_hasher.verify(hashed_password, plain_password)
        logger.debug("Password verification successful")
        return True
    except argon2.exceptions.VerifyMismatchError:
        logger.debug("Password verification failed - mismatch")
        return False
    except argon2.exceptions.VerificationError as e:
        logger.warning(f"Password verification error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during password verification: {e}")
        return False

def get_password_hash(password: str) -> str:
    """
    使用 Argon2 生成密码哈希
    
    Args:
        password: 明文密码
    
    Returns:
        Argon2 哈希后的密码
    """
    try:
        hashed = password_hasher.hash(password)
        logger.debug("Password hashed successfully with Argon2")
        return hashed
    except Exception as e:
        logger.error(f"Password hashing failed: {e}")
        raise

def decode_token(
    token: str, 
    expected_type: Optional[TokenType] = None
) -> Optional[dict]:
    """
    解码 JWT 令牌
    
    Args:
        token: JWT 令牌
        expected_type: 期望的令牌类型，如果指定则会验证
    
    Returns:
        解码后的载荷，如果失败返回 None
    """
    try:
        payload = jwt.decode(
            token, 
            settings.secret_key, 
            algorithms=[settings.algorithm]
        )
        
        # 验证令牌类型（如果指定）
        if expected_type:
            token_type = payload.get("type")
            if token_type != expected_type.value:
                logger.warning(f"Token type mismatch. Expected: {expected_type.value}, Got: {token_type}")
                return None
            
        logger.debug("Token decoded successfully")
        return payload
    except ExpiredSignatureError:
        logger.warning("Token has expired")
        return None
    except JWTError as e:
        logger.warning(f"JWT decode failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during token decode: {e}")
        return None

def generate_secure_random_string(length: int = 32) -> str:
    """
    生成安全的随机字符串
    
    Args:
        length: 字符串长度
    
    Returns:
        URL安全的随机字符串
    """
    return secrets.token_urlsafe(length)

def generate_secure_token() -> str:
    """
    生成安全令牌（用于密码重置等）
    """
    return secrets.token_urlsafe(64)

def check_password_strength(password: str) -> dict:
    """
    检查密码强度
    
    Args:
        password: 要检查的密码
    
    Returns:
        包含强度信息的字典
    """
    strength = {
        "score": 0,
        "issues": [],
        "suggestions": [],
        "is_strong": False
    }
    
    # 长度检查
    if len(password) >= 16:
        strength["score"] += 3
    elif len(password) >= 12:
        strength["score"] += 2
    elif len(password) >= 8:
        strength["score"] += 1
    else:
        strength["issues"].append("密码长度至少需要8个字符")
        strength["suggestions"].append("使用更长的密码（推荐12个字符以上）")
    
    # 字符类型检查
    has_lower = bool(re.search(r"[a-z]", password))
    has_upper = bool(re.search(r"[A-Z]", password))
    has_digit = bool(re.search(r"\d", password))
    has_special = bool(re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>?]", password))
    
    char_types = sum([has_lower, has_upper, has_digit, has_special])
    
    if char_types >= 4:
        strength["score"] += 2
    elif char_types >= 3:
        strength["score"] += 1
    
    if not has_lower:
        strength["issues"].append("缺少小写字母")
    if not has_upper:
        strength["issues"].append("缺少大写字母")
    if not has_digit:
        strength["issues"].append("缺少数字")
    if not has_special:
        strength["issues"].append("缺少特殊字符")
    
    # 常见密码模式检查
    common_patterns = [
        r"^(password|123456|qwerty|admin|letmein)",
        r"(\d{4,})",  # 连续数字
        r"([a-zA-Z])\1{2,}",  # 重复字符
    ]
    
    for pattern in common_patterns:
        if re.search(pattern, password.lower()):
            strength["score"] = max(0, strength["score"] - 2)
            strength["issues"].append("包含常见密码模式")
            strength["suggestions"].append("避免使用常见密码和重复字符")
            break
    
    # 字典词汇检查（简化版）
    common_words = ["password", "admin", "user", "login", "welcome"]
    if any(word in password.lower() for word in common_words):
        strength["score"] = max(0, strength["score"] - 1)
        strength["issues"].append("包含常见词汇")
        strength["suggestions"].append("避免使用常见单词")
    
    # 判断是否为强密码
    strength["is_strong"] = strength["score"] >= 5 and len(strength["issues"]) == 0
    
    if not strength["suggestions"]:
        if strength["is_strong"]:
            strength["suggestions"].append("密码强度良好")
        else:
            strength["suggestions"].append("建议使用更长、更复杂的密码")
    
    return strength

def need_password_rehash(hashed_password: str) -> bool:
    """
    检查 Argon2 密码是否需要重新哈希
    
    Args:
        hashed_password: 已哈希的密码
    
    Returns:
        是否需要重新哈希
    """
    try:
        return password_hasher.check_needs_rehash(hashed_password)
    except Exception as e:
        logger.error(f"Failed to check password rehash need: {e}")
        return False

def generate_api_key() -> str:
    """
    生成 API 密钥
    
    Returns:
        API 密钥字符串
    """
    return f"ore_{secrets.token_urlsafe(32)}"

def hash_api_key(api_key: str) -> str:
    """
    哈希 API 密钥（用于存储）
    
    Args:
        api_key: 原始 API 密钥
    
    Returns:
        哈希后的 API 密钥
    """
    return get_password_hash(api_key)

def verify_api_key(api_key: str, hashed_api_key: str) -> bool:
    """
    验证 API 密钥
    
    Args:
        api_key: 原始 API 密钥
        hashed_api_key: 哈希后的 API 密钥
    
    Returns:
        验证结果
    """
    return verify_password(api_key, hashed_api_key)