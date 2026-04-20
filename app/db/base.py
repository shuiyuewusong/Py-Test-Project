# 此文件供 Alembic 检测所有模型的表结构
# 每新增模型时，需在此 import

from sqlmodel import SQLModel  # noqa: F401

# 显式导入所有 SQLModel table 模型，以便 alembic autogenerate 能识别
from app.models.user import User  # noqa: F401

# 导出 metadata 供 alembic 使用
metadata = SQLModel.metadata
