# models.py

from exts import db
from datetime import datetime
from sqlalchemy import Integer, String, Text, DateTime, Date, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional


# --- 数据库模型定义 ---

class User(db.Model):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    # 密码哈希值
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default='viewer')
    email: Mapped[Optional[str]] = mapped_column(String(120), unique=True, nullable=True)


class PublicInfo(db.Model):
    __tablename__ = 'public_info'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, default='news')
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(100), nullable=False, default='社区管委会')
    publish_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    views_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default='published')

    # 建立与收益明细的一对多关系，方便查询
    revenues = db.relationship('PublicRevenue', backref='report')


class MaintenanceRecord(db.Model):
    __tablename__ = 'maintenance_record'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    facility: Mapped[str] = mapped_column(String(100), nullable=False)
    record_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default='scheduled')
    responsible_person: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)


class PublicRevenue(db.Model):
    __tablename__ = 'public_revenue'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String(10), nullable=False)  # 'income' 或 'expense'
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)
    transaction_date: Mapped[datetime.date] = mapped_column(Date, nullable=False, default=datetime.utcnow)
    party: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    # 外键关联到 PublicInfo
    report_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('public_info.id'), nullable=True)

# 为了让 Flask-Migrate 发现所有模型，它们需要在这个文件被导入。
# ----------------------------------------------------------------------