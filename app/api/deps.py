from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from app.core.security import decode_access_token
from app.crud.user import user_crud
from app.db.session import get_db
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=True)

DBSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    db: DBSession,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise credentials_exception
    user = user_crud.get(db, id=int(user_id))
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not user_crud.is_active(current_user):
        raise HTTPException(status_code=400, detail="用户已被禁用")
    return current_user


def get_current_superuser(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    if not user_crud.is_superuser(current_user):
        raise HTTPException(status_code=403, detail="权限不足，需要超级管理员")
    return current_user


CurrentUser = Annotated[User, Depends(get_current_active_user)]
SuperUser = Annotated[User, Depends(get_current_superuser)]
