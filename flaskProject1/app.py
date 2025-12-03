# app.py

from flask import Flask, render_template, redirect, url_for, flash, request
import config
from exts import db, migrate
from models import PublicInfo
# 导入两个蓝图
from blueprint.auth import auth_bp
from blueprint.admin import admin_bp  # <--- 新增导入
from models import PublicInfo, MaintenanceRecord # 记得在文件顶部导入 MaintenanceRecord
from models import PublicInfo, MaintenanceRecord, Carousel


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)

    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)  # <--- 注册 Admin 蓝图

    # --- 公共路由 ---

    @app.route("/")
    def news():
        # 1. 获取当前页码，默认为第 1 页
        page = request.args.get('page', 1, type=int)
        per_page = 5
        # 2. 构建主列表查询语句
        stmt_all = db.select(PublicInfo).order_by(PublicInfo.publish_date.desc())

        # 3. 执行分页查询 (Flask-SQLAlchemy 3.0+ 语法)
        # 这会返回一个 pagination 对象，包含 .items (当前页数据), .pages (总页数) 等信息
        stmt_all = db.select(PublicInfo).order_by(PublicInfo.publish_date.desc())
        pagination = db.paginate(stmt_all, page=page, per_page=per_page, error_out=False)

        # --- 侧边栏查询保持不变 ---
        # 侧边栏 - 维护通知
        stmt_notice = db.select(PublicInfo).where(PublicInfo.category == 'notice').order_by(
            PublicInfo.publish_date.desc()).limit(5)
        notices = db.session.execute(stmt_notice).scalars().all()

        # 侧边栏 - 安全提醒
        stmt_safety = db.select(PublicInfo).where(PublicInfo.category == 'safety').order_by(
            PublicInfo.publish_date.desc()).limit(5)
        safeties = db.session.execute(stmt_safety).scalars().all()

        # 侧边栏 - 维修记录
        stmt_record = db.select(MaintenanceRecord).order_by(MaintenanceRecord.start_date.desc()).limit(5)
        records = db.session.execute(stmt_record).scalars().all()

        stmt_carousel = db.select(Carousel).where(Carousel.is_active == True).order_by(Carousel.priority.desc(),Carousel.create_time.desc())
        carousel_list = db.session.execute(stmt_carousel).scalars().all()



        # 注意：这里传给模板的是 pagination 对象，而不是原来的 news_list
        return render_template("news.html",
                               pagination=pagination,
                               notices=notices,
                               safeties=safeties,
                               records=records,
                               carousel_list=carousel_list)

    @app.route("/login")
    def login_redirect():
        return redirect(url_for('auth.login'))

    @app.route('/static-demo')  # 改个名避免冲突，或者直接删除
    def static_demo():
        return render_template("static.html")

    # app.py

    # ... 之前的代码 ...

    # 新增：维修记录详情页路由
    @app.route('/maintenance/<int:record_id>')
    def maintenance_detail(record_id):
        # 使用 SQLAlchemy 获取记录
        # 记得确保 MaintenanceRecord 已经在文件顶部导入
        record = db.session.get(MaintenanceRecord, record_id)

        if not record:
            flash('未找到该维修记录', 'danger')
            return redirect(url_for('news'))

        return render_template("maintenance_detail.html", record=record)

    # ... 之后的代码 ...

    # 详情页依然对所有人可见
    @app.route('/detail/<int:item_id>')
    def detail(item_id):
        # 1. 获取当前文章详情
        item = db.session.get(PublicInfo, item_id)

        if not item:
            flash('未找到该文章', 'danger')
            return redirect(url_for('news'))

        # 2. 增加浏览量
        item.views_count += 1
        db.session.commit()

        # 3. 【新增】查询侧边栏数据 (相关链接)
        # 逻辑：查询 PublicInfo 表，排除当前这篇文章 (id != item_id)，按时间倒序，取前 5 条
        stmt_sidebar = db.select(PublicInfo).where(PublicInfo.id != item_id).order_by(
            PublicInfo.publish_date.desc()).limit(5)
        sidebar_list = db.session.execute(stmt_sidebar).scalars().all()

        # 4. 将 sidebar_list 传递给模板
        return render_template("detail.html", item=item, sidebar_list=sidebar_list)
    # --- 【注意】 ---
    # 旧的 /pub, /submit_publication, /edit, /update_publication
    # 已经被移除了！现在这些功能都在 /admin 蓝图下管理。

    @app.route('/feedback')
    def feedback():
        # 1. 为了保持页面右侧不空，依然查询最新的5条动态作为侧边栏
        stmt_sidebar = db.select(PublicInfo).order_by(PublicInfo.publish_date.desc()).limit(5)
        sidebar_list = db.session.execute(stmt_sidebar).scalars().all()

        # 2. 渲染专门的反馈模板
        return render_template("feedback.html", sidebar_list=sidebar_list)


    return app



app = create_app()

if __name__ == '__main__':
    app.run(debug=True)