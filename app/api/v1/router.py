from fastapi import APIRouter

from app.api.v1.endpoints import health, sql_test, users

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["健康检查"])
api_router.include_router(users.router, prefix="/users", tags=["用户管理"])
api_router.include_router(sql_test.router, prefix="/test", tags=["SQL示例接口"])
