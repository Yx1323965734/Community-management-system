# exts.py

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData
from flask_migrate import Migrate

# 定义命名约定元数据
naming_convention = {
    'ix': 'ix_%(column_0_label)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(column_0_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'pk': 'pk_%(table_name)s'
}

# 继承您的 Base 类定义
class CustomBase(DeclarativeBase):
    metadata = MetaData(naming_convention=naming_convention)

# 初始化 SQLAlchemy 实例，但不传递 app 实例
db = SQLAlchemy(model_class=CustomBase)

# 初始化 Migrate 实例
migrate = Migrate()