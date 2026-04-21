from typing import Literal
from urllib.parse import quote_plus

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # -------------------------
    # 应用基础配置
    # -------------------------
    APP_ENV: Literal["development", "production", "testing"] = "development"
    APP_DEBUG: bool = False
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    PROJECT_NAME: str = "Test-Project"
    # API_V1_STR: str = "/api"

    # -------------------------
    # 安全配置
    # -------------------------
    SECRET_KEY: str = "change-me-in-production-use-openssl-rand-hex-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # -------------------------
    # 数据库类型：mysql 或 dameng
    # -------------------------
    DB_TYPE: Literal["mysql", "dameng"] = "mysql"

    # -------------------------
    # MySQL 配置
    # -------------------------
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = "mydb"
    MYSQL_POOL_SIZE: int = 10
    MYSQL_MAX_OVERFLOW: int = 20
    MYSQL_POOL_RECYCLE: int = 3600

    # -------------------------
    # 达梦数据库配置
    # -------------------------
    DM_HOST: str = "localhost"
    DM_PORT: int = 5236
    DM_USER: str = "SYSDBA"
    DM_PASSWORD: str = "SYSDBA001"
    DM_DATABASE: str = "SYSDBA"
    DM_POOL_SIZE: int = 10
    DM_MAX_OVERFLOW: int = 20
    DM_POOL_RECYCLE: int = 3600

    @property
    def DATABASE_URL(self) -> str:
        """根据 DB_TYPE 动态生成数据库连接 URL"""
        if self.DB_TYPE == "mysql":
            encoded_password = quote_plus(self.MYSQL_PASSWORD)
            return (
                f"mysql+pymysql://{self.MYSQL_USER}:{encoded_password}"
                f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
                "?charset=utf8mb4"
            )
        if self.DB_TYPE == "dameng":
            # 需要安装 dmPython 驱动和 sqlalchemy-dm dialect
            # pip install sqlalchemy-dm
            # dmPython 需从达梦服务器安装包获取
            return (
                f"dm+dmPython://{self.DM_USER}:{self.DM_PASSWORD}"
                f"@{self.DM_HOST}:{self.DM_PORT}/{self.DM_DATABASE}"
            )
        raise ValueError(f"不支持的数据库类型: {self.DB_TYPE}")

    @property
    def DB_POOL_SIZE(self) -> int:
        return self.MYSQL_POOL_SIZE if self.DB_TYPE == "mysql" else self.DM_POOL_SIZE

    @property
    def DB_MAX_OVERFLOW(self) -> int:
        return self.MYSQL_MAX_OVERFLOW if self.DB_TYPE == "mysql" else self.DM_MAX_OVERFLOW

    @property
    def DB_POOL_RECYCLE(self) -> int:
        return self.MYSQL_POOL_RECYCLE if self.DB_TYPE == "mysql" else self.DM_POOL_RECYCLE

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_must_be_set(cls, v: str) -> str:
        if v == "change-me-in-production-use-openssl-rand-hex-32":
            import warnings
            warnings.warn("SECRET_KEY 使用默认值，生产环境请务必修改！", stacklevel=2)
        return v


settings = Settings()
