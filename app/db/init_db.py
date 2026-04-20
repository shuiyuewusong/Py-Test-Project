import logging

from sqlmodel import Session

from app.core.security import get_password_hash
from app.crud.user import user_crud
from app.db.session import engine
from app.models.user import User
from app.schemas.user import UserCreate

logger = logging.getLogger(__name__)


def init_db(db: Session) -> None:
    """初始化数据库：创建默认超级管理员账号（仅首次运行）"""
    existing = user_crud.get_by_email(db, email="admin@example.com")
    if existing:
        logger.info("初始化跳过：admin 账号已存在")
        return

    admin = UserCreate(
        email="admin@example.com",
        username="admin",
        password="Admin@123456",
        is_superuser=True,
    )
    user_crud.create(db, obj_in=admin)
    logger.info("初始化完成：已创建默认 admin 账号（admin@example.com / Admin@123456）")
