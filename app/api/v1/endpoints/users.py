from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, DBSession, SuperUser
from app.core.security import create_access_token
from app.crud.user import user_crud
from app.schemas.user import (
    LoginRequest,
    Token,
    UserCreate,
    UserDetailRequest,
    UserListRequest,
    UserListResponse,
    UserPublic,
    UserUpdate,
    UserDetailRequest as UserDeleteRequest,
)

router = APIRouter()


@router.post("/login", response_model=Token, summary="用户登录")
def login(db: DBSession, body: LoginRequest) -> Token:
    user = user_crud.authenticate(db, email=body.email, password=body.password)
    if not user:
        raise HTTPException(status_code=401, detail="邮箱或密码错误")
    if not user_crud.is_active(user):
        raise HTTPException(status_code=400, detail="用户已被禁用")
    return Token(access_token=create_access_token(subject=user.id))


@router.post("/register", response_model=UserPublic, summary="注册用户")
def register(db: DBSession, body: UserCreate) -> UserPublic:
    if user_crud.get_by_email(db, email=body.email):
        raise HTTPException(status_code=400, detail="该邮箱已注册")
    if user_crud.get_by_username(db, username=body.username):
        raise HTTPException(status_code=400, detail="该用户名已被占用")
    return user_crud.create(db, obj_in=body)


@router.post("/info", response_model=UserPublic, summary="获取当前用户信息")
def user_info(current_user: CurrentUser) -> UserPublic:
    return UserPublic.model_validate(current_user)


@router.post("/update", response_model=UserPublic, summary="更新当前用户信息")
def update_user(db: DBSession, current_user: CurrentUser, body: UserUpdate) -> UserPublic:
    return user_crud.update(db, db_obj=current_user, obj_in=body)


@router.post("/list", response_model=UserListResponse, summary="用户列表（管理员）")
def list_users(db: DBSession, _: SuperUser, body: UserListRequest) -> UserListResponse:
    total = user_crud.count(db)
    items = user_crud.get_multi(db, skip=body.skip, limit=body.limit)
    return UserListResponse(total=total, items=items)


@router.post("/detail", response_model=UserPublic, summary="获取指定用户（管理员）")
def user_detail(db: DBSession, _: SuperUser, body: UserDetailRequest) -> UserPublic:
    user = user_crud.get(db, id=body.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@router.post("/delete", summary="删除用户（管理员）")
def delete_user(db: DBSession, current_user: SuperUser, body: UserDeleteRequest) -> dict:
    if current_user.id == body.user_id:
        raise HTTPException(status_code=400, detail="不能删除自己")
    user = user_crud.remove(db, id=body.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"message": "删除成功"}
