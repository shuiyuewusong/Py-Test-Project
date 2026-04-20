from datetime import datetime
from typing import Optional

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class LoginRequest(SQLModel):
    """登录请求体"""
    email: EmailStr
    password: str


class UserCreate(SQLModel):
    """注册用户请求体"""
    email: EmailStr
    username: str = Field(min_length=2, max_length=100)
    password: str = Field(min_length=6, max_length=128)
    full_name: Optional[str] = Field(default=None, max_length=100)
    is_superuser: bool = False


class UserUpdate(SQLModel):
    """更新当前用户请求体（字段均可选）"""
    full_name: Optional[str] = Field(default=None, max_length=100)
    password: Optional[str] = Field(default=None, min_length=6, max_length=128)
    is_active: Optional[bool] = None


class UserDetailRequest(SQLModel):
    """获取/删除指定用户请求体"""
    user_id: int


class UserListRequest(SQLModel):
    """用户列表分页请求体"""
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


class UserPublic(SQLModel):
    """用户公开信息（响应体）"""
    id: int
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    is_superuser: bool
    created_at: datetime


class UserListResponse(SQLModel):
    """用户列表分页响应"""
    total: int
    items: list[UserPublic]


class Token(SQLModel):
    """JWT Token 响应"""
    access_token: str
    token_type: str = "bearer"
