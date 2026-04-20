from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,
    pool_recycle=settings.DB_POOL_RECYCLE,
    echo=settings.APP_DEBUG,
)

# class_=Session 使用 SQLModel 的 Session，支持 .exec() 方法
SessionLocal = sessionmaker(class_=Session, autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI 依赖注入：提供数据库会话，请求结束后自动关闭"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> bool:
    """检查数据库连接是否正常"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
