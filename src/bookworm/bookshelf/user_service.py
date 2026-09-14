"""用户服务 - 匿名用户初始化 & 注册"""

import uuid
import hashlib
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from .models import User, Book, ReadingRecord


def _hash_password(password: str) -> str:
    """简单密码哈希 (SHA256 + salt), 生产环境应使用 bcrypt"""
    salt = "bookworm_salt_2024"
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()


def get_or_create_anonymous_user(db: Session, device_id: str) -> User:
    """
    根据 device_id 获取或创建匿名用户.

    device_id 由前端根据浏览器指纹生成, 同一设备总是生成相同的 ID.
    如果该 device_id 对应的用户已存在, 直接返回; 否则创建新匿名用户.
    """
    user = db.query(User).filter(User.user_id == device_id).first()
    if user:
        return user

    user = User(
        user_id=device_id,
        name="书架主人",
        is_anonymous=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def register_user(
    db: Session,
    device_id: str,
    phone: str,
    password: str,
    name: str = "书架主人",
) -> User:
    """
    注册正式用户.

    1. 检查手机号是否已被注册
    2. 将 device_id 对应的匿名用户升级为正式用户
    3. 填充 phone, password_hash, name, is_anonymous=False
    """
    # 检查手机号是否已存在
    existing = db.query(User).filter(User.phone == phone).first()
    if existing:
        raise ValueError("该手机号已注册")

    # 找到匿名用户
    user = db.query(User).filter(User.user_id == device_id).first()
    if not user:
        raise ValueError("用户不存在, 请先初始化")

    if not user.is_anonymous:
        raise ValueError("该用户已注册")

    # 升级为正式用户
    user.phone = phone
    user.password_hash = _hash_password(password)
    user.name = name
    user.is_anonymous = False
    user.updated_at = datetime.now()

    db.commit()
    db.refresh(user)
    return user


def login_user(db: Session, phone: str, password: str) -> Optional[User]:
    """
    登录验证.

    返回 User 对象如果验证成功, 否则返回 None.
    """
    user = db.query(User).filter(User.phone == phone).first()
    if not user:
        return None
    if user.is_anonymous:
        return None
    if user.password_hash != _hash_password(password):
        return None
    return user
