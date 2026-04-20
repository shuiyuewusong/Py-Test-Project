"""Alembic 迁移环境配置

运行方式：
  生成迁移：alembic revision --autogenerate -m "描述"
  执行迁移：alembic upgrade head
  回滚：    alembic downgrade -1
"""

import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# 将项目根目录加入 sys.path，确保能 import app 包
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings
from app.db.base import metadata  # noqa: F401 — 触发所有模型的导入

# Alembic Config 对象
config = context.config

# 设置日志
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 使用 .env 中的数据库 URL 覆盖 alembic.ini 中的占位
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

target_metadata = metadata


def run_migrations_offline() -> None:
    """在"离线"模式下运行迁移（不需要数据库连接，仅生成 SQL 脚本）"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """在"在线"模式下运行迁移（直接连接数据库执行）"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
