from fastapi import APIRouter
from app.api.deps import CurrentUser, DBSession, SuperUser
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


@router.post("/info", response_model=UserListResponse, summary="获取所有用户信息")
def user_info(current_user: CurrentUser) -> UserListResponse:
    # user_crud.
    return UserPublic.model_validate(current_user)
