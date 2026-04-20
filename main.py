from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化，关闭时清理"""
    setup_logging()

    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"启动 {settings.PROJECT_NAME} [{settings.APP_ENV}] — DB: {settings.DB_TYPE}")

    # 可在此执行数据库表创建（开发环境）或检查连接
    # 生产环境建议使用 alembic upgrade head 管理表结构
    if settings.APP_ENV == "development":
        from sqlmodel import SQLModel
        from app.db.session import engine
        from app.db import base  # noqa: 触发所有模型导入
        SQLModel.metadata.create_all(engine)

    yield

    logger.info(f"关闭 {settings.PROJECT_NAME}")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    docs_url="/docs" if settings.APP_ENV != "production" else None,
    redoc_url="/redoc" if settings.APP_ENV != "production" else None,
    openapi_url="/openapi.json" if settings.APP_ENV != "production" else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.APP_ENV == "development" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix='/api')


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_ENV == "development",
    )
