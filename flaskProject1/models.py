from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# 初始化 SQLAlchemy 实例
# 假设您在应用配置中设置了数据库URI，并在应用工厂中传入了 app
db = SQLAlchemy()


# --- 1. 核心信息发布模型 (News/Reports/Notices) ---
# 用于存储新闻动态、收益报告、维护通知等所有公开发布的内容。
class PublicInfo(db.Model):
    """社区公共信息模型，用于存储新闻、公告、报告等。"""

    __tablename__ = 'public_info'

    id = db.Column(db.Integer, primary_key=True)

    # 标题，不允许为空
    title = db.Column(db.String(255), nullable=False)

    # 内容类型：'news'(新闻), 'report'(收益报告), 'notice'(通知), 'safety'(安全提醒)
    category = db.Column(db.String(50), nullable=False, default='news')

    # 简短摘要
    summary = db.Column(db.Text, nullable=True)

    # 正文内容
    content = db.Column(db.Text, nullable=False)

    # 发布者/作者
    author = db.Column(db.String(100), nullable=False, default='社区管委会')

    # 发布日期
    publish_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # 浏览次数/阅读量 (可用于侧边栏热门排序)
    views_count = db.Column(db.Integer, default=0)

    # 状态：'published'(已发布), 'draft'(草稿)
    status = db.Column(db.String(20), default='published')

    def __repr__(self):
        return f"<PublicInfo {self.id}: {self.title}>"


# --- 2. 维修和维护记录模型 ---
# 用于存储设施维修和定期维护的详细记录 (对应侧边栏的 维护通知 和 维修记录)
class MaintenanceRecord(db.Model):
    """社区维修与维护记录模型。"""

    __tablename__ = 'maintenance_record'

    id = db.Column(db.Integer, primary_key=True)

    # 记录名称或标题
    title = db.Column(db.String(255), nullable=False)

    # 设施名称/位置 (如：'3号楼电梯', '地下车库照明', '供水系统')
    facility = db.Column(db.String(100), nullable=False)

    # 记录类型：'repair'(维修), 'schedule'(定期维护)
    record_type = db.Column(db.String(50), nullable=False)

    # 详细描述/问题描述
    description = db.Column(db.Text, nullable=True)

    # 计划开始/实际开始时间
    start_date = db.Column(db.DateTime, nullable=False)

    # 计划结束/实际结束时间
    end_date = db.Column(db.DateTime, nullable=True)

    # 状态：'in-progress'(进行中), 'completed'(已完成), 'scheduled'(已计划)
    status = db.Column(db.String(50), default='scheduled')

    # 负责人/维修公司
    responsible_person = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"<MaintenanceRecord {self.id}: {self.title} - {self.status}>"


# --- 3. 社区公共收益模型 ---
# 用于存储每一笔收入和支出明细，对应收益管理和公示
class PublicRevenue(db.Model):
    """社区公共收益明细模型。"""

    __tablename__ = 'public_revenue'

    id = db.Column(db.Integer, primary_key=True)

    # 交易类型：'income'(收入), 'expense'(支出)
    type = db.Column(db.String(10), nullable=False)

    # 交易描述 (如：'停车场收费', '儿童游乐场设施升级')
    description = db.Column(db.String(255), nullable=False)

    # 金额 (使用 Decimal 类型以保证财务精度)
    amount = db.Column(db.Numeric(10, 2), nullable=False)

    # 发生日期
    transaction_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)

    # 来源/去向 (如：'XX广告公司', 'YY维修公司')
    party = db.Column(db.String(150), nullable=True)

    # 对应的季度/年度报告ID (外键关联到 PublicInfo，如果需要)
    report_id = db.Column(db.Integer, db.ForeignKey('public_info.id'), nullable=True)

    def __repr__(self):
        return f"<PublicRevenue {self.id}: {self.type} {self.amount}>"


# --- 4. 用户/管理员模型 ---
# 用于登录功能 (login.html)
class User(db.Model):
    """系统用户模型，用于登录和权限管理。"""

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)  # 存储密码哈希值

    # 权限级别：'admin'(管理员), 'editor'(编辑), 'viewer'(查看者)
    role = db.Column(db.String(50), default='viewer')

    email = db.Column(db.String(120), unique=True, nullable=True)

    def __repr__(self):
        return f"<User {self.username}>"

# ----------------------------------------------------------------------
# 注意：在实际应用中，您需要进一步配置 Flask 应用，并执行以下操作：
# 1. 在 Flask 配置中设置 SQLALCHEMY_DATABASE_URI。
# 2. 在应用工厂中：
#    app = Flask(__name__)
#    app.config.from_object('config')
#    db.init_app(app)
# 3. 在命令行或脚本中运行数据库迁移工具 (如 Flask-Migrate) 来创建表。