# create_db.py
from app import create_app
from exts import db
# 必须导入模型，否则 SQLAlchemy 此时无法识别 Carousel
from models import Carousel

app = create_app()

with app.app_context():
    # create_all 会检测数据库，如果发现有新定义的模型（如Carousel）但在数据库里没有表，它会自动创建
    db.create_all()
    print(">>> 数据库表更新成功！Carousel 表已创建。")