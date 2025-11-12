from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import text
import config
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import MetaData, Integer, String, Text, DateTime, Date, Numeric, ForeignKey
from typing import Optional # 用于 Optional 类型提示

app = Flask(__name__)
app.config.from_object(config)

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention={
        'ix': 'ix_%(column_0_label)s',
        'uq': 'uq_%(table_name)s_%(column_0_name)s',
        'ck': 'ck_%(table_name)s_%(column_0_name)s',
        'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
        'pk': 'pk_%(table_name)s'
    })

db = SQLAlchemy(app=app, model_class=Base)

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
    # 使用 DateTime 并设置默认值为当前时间
    publish_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    views_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default='published')

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
    type: Mapped[str] = mapped_column(String(10), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)
    # 使用 Date 类型，仅存储日期
    transaction_date: Mapped[datetime.date] = mapped_column(Date, nullable=False, default=datetime.utcnow)
    party: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    # 外键关联
    report_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('public_info.id'), nullable=True)

# --- 数据库初始化 ---
with app.app_context():
    db.create_all()

# --- 路由定义 ---

@app.route("/")
def news():
    # 实际应用中：从 PublicInfo 获取新闻列表并传递
    return render_template("news.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route('/static')
def static_demo():
    return render_template("static.html")

@app.route('/pub')
def pub():
    # 传递当前日期，用于 pub.html 中的 JavaScript 逻辑
    return render_template("pub.html", today=datetime.now().strftime('%Y-%m-%d'))

# detail 路由需要一个 item 对象
@app.route('/detail/<int:item_id>')
@app.route('/detail')
def detail(item_id=1):
    # 模拟从数据库获取的 item 对象
    # 在 detail.html 中，我们使用硬编码的数据，这里仅为演示传递 item
    mock_item = {
        'id': item_id,
        'title': '社区公共收益第一季度公示报告发布',
        'author': '社区管委会',
        'publish_date': '2023-04-15',
        'views_count': 1258,
        # ... 其他字段
    }
    return render_template("detail.html", item=mock_item)

# edit 路由需要一个 item 对象
@app.route('/edit/<int:item_id>')
@app.route('/edit')
def edit(item_id=1):
    # 模拟从数据库获取的待编辑 item 对象
    mock_item = {
        'id': item_id,
        'title': '社区公共收益第一季度公示报告发布 (待修改)',
        'category': 'report', # 确保 category 匹配 select 选项
        'author': '社区管委会',
        'date': '2023-04-15',
        'summary': '本季度社区公共收益主要来源于停车场收费、公共区域广告和社区活动场地租赁等...',
        'content': '尊敬的社区居民：为确保社区公共收益的透明化管理，社区管委会特此发布《社区公共收益第一季度公示报告》。本报告涵盖了2023年1月1日至2023年3月31日期间的全部收入与支出情况。详细财务明细已同步公示于社区公告栏及本系统的**收益公示**板块...',
    }
    return render_template("edit.html", item_id=item_id, item=mock_item)

if __name__ == '__main__':
    app.run(debug=True)