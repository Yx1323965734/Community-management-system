# seed.py

from app import create_app
from exts import db
# 导入所有模型以便脚本能够访问它们
from models import User, PublicInfo, MaintenanceRecord, PublicRevenue
from datetime import datetime, date
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text  # 导入 text 用于手动清除表（可选，但更健壮）

# 初始化 Flask 应用
app = create_app()


def seed_data():
    """清除现有数据并插入新的测试数据"""
    with app.app_context():
        print("--- 正在尝试清除现有数据... ---")

        # 使用更安全的 TRUNCATE 或 DELETE FROM 语句清除数据
        try:
            # SQLAlchemy 的 delete() 方式，但对于测试数据，直接删除并重新创建可能更快
            db.session.query(PublicRevenue).delete()
            db.session.query(MaintenanceRecord).delete()
            db.session.query(PublicInfo).delete()
            db.session.query(User).delete()
            db.session.commit()
            print("--- 数据清除完成。正在插入新的测试数据... ---")
        except Exception as e:
            db.session.rollback()
            print(f"!!! 清除数据失败: {e}. 可能会出现主键冲突。!!!")

        # ------------------- 1. 用户数据 (User) -------------------
        hashed_password = generate_password_hash('admin123')
        user_list = [
            User(username='admin', password_hash=hashed_password, role='admin', email='admin@community.com'),
            User(username='viewer01', password_hash=generate_password_hash('view123'), role='viewer',
                 email='viewer@community.com'),
        ]
        db.session.add_all(user_list)

        # ------------------- 2. 公共信息 (PublicInfo) -------------------

        # 注意：这里我们先定义报告，以便后续 PublicRevenue 可以引用它的 ID
        q1_report = PublicInfo(
            title='社区公共收益第一季度公示报告',
            category='report',
            summary='本季度公共收益总收入达到28.5万元，同比增长15%。',
            content='详细的财务明细账目已同步公示于社区公告栏及本系统的收益公示板块，欢迎广大居民查阅监督。',
            publish_date=datetime(2023, 4, 15, 10, 30),
            author='社区管委会',
            views_count=500
        )
        db.session.add(q1_report)
        db.session.flush()  # 立即获取 q1_report 的 ID

        info_list = [
            PublicInfo(
                title='社区公共设施升级改造项目启动',
                category='news',
                summary='经居民代表大会决议，将使用部分公共收益对社区儿童游乐场和健身区域进行升级改造。',
                content='项目预计投资15万元，计划于5月初开工，6月底完工。',
                publish_date=datetime(2023, 4, 10, 15, 0),
                author='社区管委会',
                views_count=320
            ),
            PublicInfo(
                title='夏季用电安全注意事项提醒',
                category='safety',
                summary='提醒居民注意夏季用电安全，避免电器超负荷。',
                content='请勿私拉电线，电动车请在集中充电区域充电。',
                publish_date=datetime.now(),
                author='物业管理处',
                views_count=150
            ),
        ]
        db.session.add_all(info_list)

        # ------------------- 3. 维护记录 (MaintenanceRecord) -------------------
        maintenance_list = [
            MaintenanceRecord(
                title='3号楼电梯故障已修复',
                facility='3号楼电梯',
                record_type='repair',
                description='电梯主板损坏已更换。',
                start_date=datetime(2023, 5, 12),
                end_date=datetime(2023, 5, 13),
                status='completed',
                responsible_person='A维修公司'
            ),
            MaintenanceRecord(
                title='地下车库照明检修',
                facility='地下车库照明',
                record_type='schedule',
                description='更换了所有故障灯具，并检查线路。',
                start_date=datetime(2023, 5, 1),
                end_date=None,  # 进行中可以不设结束时间
                status='in-progress',
                responsible_person='物业工程师'
            ),
        ]
        db.session.add_all(maintenance_list)

        # ------------------- 4. 收益明细 (PublicRevenue) -------------------
        revenue_list = [
            PublicRevenue(
                type='income',
                description='停车场收费 (Q1)',
                amount=250000.00,
                transaction_date=date(2023, 4, 1),
                report_id=q1_report.id  # 关联到第一季度报告
            ),
            PublicRevenue(
                type='income',
                description='公共区域广告位租金',
                amount=35000.00,
                transaction_date=date(2023, 3, 20),
                party='XX广告公司'
            ),
            PublicRevenue(
                type='expense',
                description='儿童游乐场设施采购费',
                amount=150000.00,
                transaction_date=date(2023, 5, 5),
                party='YY建材公司'
            ),
        ]
        db.session.add_all(revenue_list)

        try:
            db.session.commit()
            print("\n--- 所有测试数据成功插入数据库。---")
        except IntegrityError as e:
            db.session.rollback()
            print(f"\n--- 插入失败，可能存在重复的主键或唯一约束冲突。请检查您的数据和模型。---\n错误: {e}")


if __name__ == '__main__':
    seed_data()