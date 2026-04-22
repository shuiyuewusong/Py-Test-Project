from typing import Optional

from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from sqlmodel import SQLModel

from app.api.deps import DBSession

router = APIRouter()


# ──────────────────────────────────────────────
# 无参查询
# ──────────────────────────────────────────────

@router.get("/users/all", summary="【无参】查询所有用户")
def get_all_users(db: DBSession) -> list[dict]:
    """直接用 SQL 查询 users 表全部记录（不返回密码字段）"""
    sql = text("SELECT id, email, username, full_name, is_active, is_superuser, created_at, updated_at FROM users")
    rows = db.execute(sql).mappings().all()
    return [dict(row) for row in rows]


@router.get("/users/count", summary="【无参】查询用户总数")
def get_user_count(db: DBSession) -> dict:
    """统计 users 表总行数"""
    sql = text("SELECT COUNT(*) AS total FROM users")
    result = db.execute(sql).mappings().one()
    return dict(result)


@router.get("/users/active", summary="【无参】查询所有启用状态的用户")
def get_active_users(db: DBSession) -> list[dict]:
    """固定条件：is_active = 1，无需调用方传参"""
    sql = text(
        "SELECT id, email, username, full_name, created_at "
        "FROM users WHERE is_active = 1 ORDER BY id"
    )
    rows = db.execute(sql).mappings().all()
    return [dict(row) for row in rows]


# ──────────────────────────────────────────────
# 有参查询
# ──────────────────────────────────────────────

@router.get("/users/by-id/{user_id}", summary="【有参-路径参数】按 ID 查询用户")
def get_user_by_id(user_id: int, db: DBSession) -> dict:
    """路径参数方式：/users/by-id/1"""
    sql = text(
        "SELECT id, email, username, full_name, is_active, is_superuser, created_at "
        "FROM users WHERE id = :user_id"
    )
    row = db.execute(sql, {"user_id": user_id}).mappings().one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return dict(row)


@router.post("/users/by-email", summary="【有参-Query参数】按邮箱查询用户")
def get_user_by_email(email: str, db: DBSession) -> dict:
    """Query 参数方式：/users/by-email?email=xxx@example.com"""
    sql = text(
        "SELECT id, email, username, full_name, is_active, created_at "
        "FROM users WHERE email = :email"
    )
    row = db.execute(sql, {"email": email}).mappings().one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return dict(row)


@router.get("/users/search", summary="【有参-多Query参数】模糊搜索用户")
def search_users(
    db: DBSession,
    keyword: Optional[str] = None,
    is_active: Optional[bool] = None,
    limit: int = 10,
    offset: int = 0,
) -> dict:
    """
    可选参数组合搜索：
    - keyword：模糊匹配 username 或 email
    - is_active：过滤启用/禁用状态
    - limit / offset：分页
    """
    conditions = ["1=1"]
    params: dict = {"limit": limit, "offset": offset}

    if keyword:
        conditions.append("(username LIKE :kw OR email LIKE :kw)")
        params["kw"] = f"%{keyword}%"

    if is_active is not None:
        conditions.append("is_active = :is_active")
        params["is_active"] = int(is_active)

    where = " AND ".join(conditions)
    sql = text(
        f"SELECT id, email, username, full_name, is_active, created_at "
        f"FROM users WHERE {where} ORDER BY id LIMIT :limit OFFSET :offset"
    )
    count_sql = text(f"SELECT COUNT(*) AS total FROM users WHERE {where}")

    rows = db.execute(sql, params).mappings().all()
    total = db.execute(count_sql, {k: v for k, v in params.items() if k not in ("limit", "offset")}).scalar()

    return {"total": total, "items": [dict(r) for r in rows]}


@router.post("/users/batch-ids", summary="【有参-Body参数】按 ID 列表批量查询")
def get_users_by_ids(ids: list[int], db: DBSession) -> list[dict]:
    """
    Body 传入 ID 列表，例如：[1, 2, 3]
    注意：IN 子句用占位符拼接，防止 SQL 注入
    """
    if not ids:
        return []
    placeholders = ", ".join(f":id_{i}" for i in range(len(ids)))
    params = {f"id_{i}": v for i, v in enumerate(ids)}
    sql = text(
        f"SELECT id, email, username, full_name, is_active, created_at "
        f"FROM users WHERE id IN ({placeholders}) ORDER BY id"
    )
    rows = db.execute(sql, params).mappings().all()
    return [dict(row) for row in rows]


# ──────────────────────────────────────────────
# Body JSON 入参查询
# ──────────────────────────────────────────────

class UserQueryRequest(SQLModel):
    """Body JSON 查询条件（所有字段均可选，组合过滤）"""
    id: Optional[int] = None
    email: Optional[str] = None
    username: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    limit: int = 10
    offset: int = 0


@router.post("/users/query", summary="【有参-Body JSON】条件查询用户")
def query_users(req: UserQueryRequest, db: DBSession) -> dict:
    """
    通过 Body JSON 传入过滤条件，所有字段可选，支持分页。
    示例请求体：
    {
        "username": "admin",
        "is_active": true,
        "limit": 5,
        "offset": 0
    }
    """
    conditions = ["1=1"]
    params: dict = {"limit": req.limit, "offset": req.offset}

    if req.id is not None:
        conditions.append("id = :id")
        params["id"] = req.id

    if req.email is not None:
        conditions.append("email LIKE :email")
        params["email"] = f"%{req.email}%"

    if req.username is not None:
        conditions.append("username LIKE :username")
        params["username"] = f"%{req.username}%"

    if req.is_active is not None:
        conditions.append("is_active = :is_active")
        params["is_active"] = int(req.is_active)

    if req.is_superuser is not None:
        conditions.append("is_superuser = :is_superuser")
        params["is_superuser"] = int(req.is_superuser)

    where = " AND ".join(conditions)
    sql = text(
        f"SELECT id, email, username, full_name, is_active, is_superuser, created_at "
        f"FROM users WHERE {where} ORDER BY id LIMIT :limit OFFSET :offset"
    )
    count_sql = text(f"SELECT COUNT(*) AS total FROM users WHERE {where}")
    count_params = {k: v for k, v in params.items() if k not in ("limit", "offset")}

    rows = db.execute(sql, params).mappings().all()
    total = db.execute(count_sql, count_params).scalar()

    return {"total": total, "items": [dict(r) for r in rows]}
