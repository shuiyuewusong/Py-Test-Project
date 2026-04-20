from fastapi import APIRouter

from app.core.config import settings
from app.db.session import check_db_connection

router = APIRouter()


@router.post("/check", summary="健康检查")
def health_check() -> dict:
    db_ok = check_db_connection()
    return {
        "status": "ok" if db_ok else "degraded",
        "app_env": settings.APP_ENV,
        "db_type": settings.DB_TYPE,
        "db": "connected" if db_ok else "disconnected",
    }
