# app.py

from flask import Flask, render_template
from datetime import datetime
import config
# 从 exts.py 导入未绑定应用的 db 和 migrate 实例
from exts import db, migrate
# 确保导入 models.py，以便 migrate 发现所有模型
import models


# --- 应用工厂函数 (强制使用工厂模式以支持 Flask-Migrate) ---
def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    # 1. 绑定 SQLAlchemy 实例到 app
    db.init_app(app)

    # 2. 初始化 Flask-Migrate
    # 必须传入 db 实例和 app 实例
    migrate.init_app(app, db)

    # --- 路由注册 ---

    @app.route("/")
    def news():
        # ... (路由代码保持不变) ...
        return render_template("news.html")

    @app.route("/login")
    def login():
        # ...
        return render_template("login.html")

    @app.route('/static')
    def static_demo():
        # ...
        return render_template("static.html")

    @app.route('/pub')
    def pub():
        # ...
        return render_template("pub.html", today=datetime.now().strftime('%Y-%m-%d'))

    @app.route('/detail/<int:item_id>')
    @app.route('/detail')
    def detail(item_id=1):
        # ...
        mock_item = {
            'id': item_id,
            'title': '社区公共收益第一季度公示报告发布',
            'author': '社区管委会',
            'publish_date': '2023-04-15',
            'views_count': 1258,
        }
        return render_template("detail.html", item=mock_item)

    @app.route('/edit/<int:item_id>')
    @app.route('/edit')
    def edit(item_id=1):
        # ...
        mock_item = {
            'id': item_id,
            'title': '社区公共收益第一季度公示报告发布 (待修改)',
            'category': 'report',
            'author': '社区管委会',
            'date': '2023-04-15',
            'summary': '本季度社区公共收益主要来源于停车场收费、公共区域广告和社区活动场地租赁等...',
            'content': '尊敬的社区居民：为确保社区公共收益的透明化管理，社区管委会特此发布《社区公共收益第一季度公示报告》。本报告涵盖了2023年1月1日至2023年3月31日期间的全部收入与支出情况。详细财务明细已同步公示于社区公告栏及本系统的**收益公示**板块...',
        }
        return render_template("edit.html", item_id=item_id, item=mock_item)

    return app


# --- 运行部分 ---

# 实例化应用
app = create_app()

if __name__ == '__main__':
    # 移除 db.create_all()
    app.run(debug=True)