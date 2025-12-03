# blueprint/admin.py

from flask import Blueprint, render_template, request, url_for, redirect, flash, session
from exts import db
from models import PublicInfo, User, MaintenanceRecord
from datetime import datetime
from functools import wraps
from sqlalchemy import or_  # 【新增】需要导入 or_ 用于维修记录的多字段搜索
from models import PublicInfo, User, MaintenanceRecord, Carousel # 记得导入 Carousel

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# --- 1. 权限控制装饰器 ---
# 这个装饰器用于保护路由，确保只有登录且角色为 admin 的人才能访问
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查是否登录
        if 'user_id' not in session:
            flash('请先登录以访问管理后台。', 'warning')
            return redirect(url_for('auth.login'))

        # 检查是否是管理员
        user_id = session.get('user_id')
        user = db.session.get(User, user_id)
        if not user or user.role != 'admin':
            flash('权限不足：您不是管理员。', 'danger')
            return redirect(url_for('news'))  # 踢回首页

        return f(*args, **kwargs)

    return decorated_function


@admin_bp.route('/')
@admin_required
def dashboard():
    keyword = request.args.get('keyword', type=str, default='')
    category = request.args.get('category', type=str, default='')

    stmt = db.select(PublicInfo)
    if keyword:
        stmt = stmt.where(PublicInfo.title.like(f'%{keyword}%'))
    if category:
        stmt = stmt.where(PublicInfo.category == category)

    stmt = stmt.order_by(PublicInfo.publish_date.desc())
    all_info = db.session.execute(stmt).scalars().all()

    return render_template('admin/dashboard.html',
                           info_list=all_info,
                           current_keyword=keyword,
                           current_category=category,
                           page_title="综合概览")

# 2. 通用辅助函数：按分类获取信息列表
def get_info_by_category_with_search(category_name):
    # 自动从请求中获取 keyword
    keyword = request.args.get('keyword', type=str, default='')

    # 基础查询：限定分类
    stmt = db.select(PublicInfo).where(PublicInfo.category == category_name)

    # 如果有关键字，叠加标题搜索条件
    if keyword:
        stmt = stmt.where(PublicInfo.title.like(f'%{keyword}%'))

    stmt = stmt.order_by(PublicInfo.publish_date.desc())
    return db.session.execute(stmt).scalars().all()

# --- 各个模块的专属路由 ---
@admin_bp.route('/news')
@admin_required
def manage_news():
    # 使用带搜索功能的辅助函数
    data = get_info_by_category_with_search('news')
    return render_template('admin/dashboard.html',
                           info_list=data,
                           page_title="新闻动态管理",
                           current_category='news',  # 标记当前分类
                           current_keyword=request.args.get('keyword', ''))  # 回显关键字


@admin_bp.route('/notices')
@admin_required
def manage_notices():
    data = get_info_by_category_with_search('notice')
    return render_template('admin/dashboard.html',
                           info_list=data,
                           page_title="维护通知管理",
                           current_category='notice',
                           current_keyword=request.args.get('keyword', ''))


@admin_bp.route('/safety')
@admin_required
def manage_safety():
    data = get_info_by_category_with_search('safety')
    return render_template('admin/dashboard.html',
                           info_list=data,
                           page_title="安全提醒管理",
                           current_category='safety',
                           current_keyword=request.args.get('keyword', ''))


@admin_bp.route('/revenue')
@admin_required
def manage_revenue():
    data = get_info_by_category_with_search('report')
    return render_template('admin/dashboard.html',
                           info_list=data,
                           page_title="收益公示管理",
                           current_category='report',
                           current_keyword=request.args.get('keyword', ''))


# --- 维修记录管理 (添加搜索) ---
@admin_bp.route('/maintenance')
@admin_required
def manage_maintenance():
    keyword = request.args.get('keyword', type=str, default='')

    stmt = db.select(MaintenanceRecord)

    if keyword:
        # 维修记录搜索：同时搜“标题”和“设施名称”
        stmt = stmt.where(or_(
            MaintenanceRecord.title.like(f'%{keyword}%'),
            MaintenanceRecord.facility.like(f'%{keyword}%')
        ))

    stmt = stmt.order_by(MaintenanceRecord.start_date.desc())
    records = db.session.execute(stmt).scalars().all()

    return render_template('admin/dashboard.html',
                           maintenance_list=records,
                           page_title="维修记录管理",
                           is_maintenance=True,
                           current_keyword=keyword)
# --- 3. 发布信息 (迁移自 app.py /pub) ---
# 合并了 GET (显示表单) 和 POST (提交数据)
@admin_bp.route('/publish', methods=['GET', 'POST'])
@admin_required
def publish():
    if request.method == 'GET':
        today = datetime.now().strftime('%Y-%m-%d')
        return render_template("pub.html", today=today)

    # 处理 POST 请求
    title = request.form.get('title')
    category = request.form.get('category')
    author = request.form.get('author')
    summary = request.form.get('summary')
    content = request.form.get('content')
    date_str = request.form.get('date')  # 获取日期字符串

    # 转换日期格式 (防止报错)
    try:
        publish_date = datetime.strptime(date_str, '%Y-%m-%d')
    except:
        publish_date = datetime.now()

    new_info = PublicInfo(
        title=title,
        category=category,
        author=author,
        summary=summary,
        content=content,
        publish_date=publish_date
    )

    db.session.add(new_info)
    db.session.commit()

    flash('发布成功！', 'success')
    return redirect(url_for('admin.dashboard'))


# --- 4. 修改信息 (迁移自 app.py /edit) ---
@admin_bp.route('/edit/<int:item_id>', methods=['GET', 'POST'])
@admin_required
def edit(item_id):
    item = db.session.get(PublicInfo, item_id)
    if not item:
        flash('文章不存在', 'danger')
        return redirect(url_for('admin.dashboard'))

    if request.method == 'GET':
        return render_template("edit.html", item_id=item_id, item=item)

    # 处理 POST 请求
    item.title = request.form.get('title')
    item.category = request.form.get('category')
    item.author = request.form.get('author')
    item.summary = request.form.get('summary')
    item.content = request.form.get('content')

    # 如果你也想允许修改日期：
    date_str = request.form.get('date')
    if date_str:
        try:
            item.publish_date = datetime.strptime(date_str, '%Y-%m-%d')
        except:
            pass

    db.session.commit()
    flash('修改已保存。', 'success')
    return redirect(url_for('admin.dashboard'))


# --- 5. 删除信息 (新功能) ---
@admin_bp.route('/delete/<int:item_id>')
@admin_required
def delete(item_id):
    item = db.session.get(PublicInfo, item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
        flash('删除成功。', 'success')
    else:
        flash('未找到该条目。', 'danger')

    return redirect(url_for('admin.dashboard'))


# --- 维修记录：添加 ---
@admin_bp.route('/maintenance/add', methods=['GET', 'POST'])
@admin_required
def maintenance_add():
    if request.method == 'GET':
        return render_template('admin/maintenance_form.html', record=None, today=datetime.now().strftime('%Y-%m-%d'))

    # 处理 POST
    new_record = MaintenanceRecord(
        title=request.form.get('title'),
        facility=request.form.get('facility'),
        record_type=request.form.get('record_type'),
        status=request.form.get('status'),
        responsible_person=request.form.get('responsible_person'),
        description=request.form.get('description'),
        # 处理开始时间
        start_date=datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
    )

    db.session.add(new_record)
    db.session.commit()

    flash('维修记录登记成功！', 'success')
    return redirect(url_for('admin.manage_maintenance'))


# --- 维修记录：编辑 ---
@admin_bp.route('/maintenance/edit/<int:record_id>', methods=['GET', 'POST'])
@admin_required
def maintenance_edit(record_id):
    record = db.session.get(MaintenanceRecord, record_id)
    if not record:
        flash('记录不存在', 'danger')
        return redirect(url_for('admin.manage_maintenance'))

    if request.method == 'GET':
        return render_template('admin/maintenance_form.html', record=record)

    # 处理更新
    record.title = request.form.get('title')
    record.facility = request.form.get('facility')
    record.record_type = request.form.get('record_type')
    record.status = request.form.get('status')
    record.responsible_person = request.form.get('responsible_person')
    record.description = request.form.get('description')

    try:
        record.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
    except:
        pass  # 如果日期格式不对，保持原样

    db.session.commit()
    flash('维修记录已更新', 'success')
    return redirect(url_for('admin.manage_maintenance'))


# --- 维修记录：删除 ---
@admin_bp.route('/maintenance/delete/<int:record_id>')
@admin_required
def maintenance_delete(record_id):
    record = db.session.get(MaintenanceRecord, record_id)
    if record:
        db.session.delete(record)
        db.session.commit()
        flash('维修记录已删除', 'success')
    else:
        flash('记录不存在', 'danger')
    return redirect(url_for('admin.manage_maintenance'))


# blueprint/admin.py

# --- 轮播图管理：列表 ---
@admin_bp.route('/carousel')
@admin_required
def manage_carousel():
    # 按优先级倒序，优先级相同的按创建时间倒序
    stmt = db.select(Carousel).order_by(Carousel.priority.desc(), Carousel.create_time.desc())
    carousels = db.session.execute(stmt).scalars().all()
    return render_template('admin/carousel_list.html', carousels=carousels)


# --- 轮播图管理：添加 ---
@admin_bp.route('/carousel/add', methods=['GET', 'POST'])
@admin_required
def carousel_add():
    if request.method == 'GET':
        return render_template('admin/carousel_form.html', item=None)

    # 处理提交
    new_item = Carousel(
        title=request.form.get('title'),
        image_url=request.form.get('image_url'),
        target_link=request.form.get('target_link'),
        priority=int(request.form.get('priority') or 0),
        is_active=True if request.form.get('is_active') else False
    )
    db.session.add(new_item)
    db.session.commit()
    flash('轮播图添加成功', 'success')
    return redirect(url_for('admin.manage_carousel'))


# --- 轮播图管理：编辑 ---
@admin_bp.route('/carousel/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def carousel_edit(id):
    item = db.session.get(Carousel, id)
    if not item:
        flash('未找到该轮播图', 'danger')
        return redirect(url_for('admin.manage_carousel'))

    if request.method == 'GET':
        return render_template('admin/carousel_form.html', item=item)

    # 更新数据
    item.title = request.form.get('title')
    item.image_url = request.form.get('image_url')
    item.target_link = request.form.get('target_link')
    item.priority = int(request.form.get('priority') or 0)
    # Checkbox如果不选，request.form里就没有这个key
    item.is_active = True if request.form.get('is_active') else False

    db.session.commit()
    flash('轮播图已更新', 'success')
    return redirect(url_for('admin.manage_carousel'))


# --- 轮播图管理：删除 ---
@admin_bp.route('/carousel/delete/<int:id>')
@admin_required
def carousel_delete(id):
    item = db.session.get(Carousel, id)
    if item:
        db.session.delete(item)
        db.session.commit()
        flash('轮播图已删除', 'success')
    return redirect(url_for('admin.manage_carousel'))