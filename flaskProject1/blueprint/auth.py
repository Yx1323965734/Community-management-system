# blueprint/auth.py

from flask import Blueprint, render_template, request, url_for, redirect, flash, session
from exts import db
from models import User

# 不需要再次导入 generate_password_hash，除非你在这个文件里用到

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # 如果已经登录，直接跳转到后台
        if 'user_id' in session:
            return redirect(url_for('admin.dashboard'))
        return render_template('login.html')

    # 处理 POST 请求
    username = request.form.get('username')
    password = request.form.get('password')

    # 1. 查询用户
    user = db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none()

    if user:
        # 【新增】严格校验：如果不是管理员，直接禁止登录
        if user.role != 'admin':
            flash('权限不足：本系统仅限管理员登录。', 'danger')
            return redirect(url_for('auth.login'))

        # 2. 验证密码
        if user.check_password(password):
            # 3. 登录成功
            session['user_id'] = user.id
            session['username'] = user.username

            # 【核心修改】这里直接跳转到管理员后台 (admin.dashboard)
            return redirect(url_for('admin.dashboard'))
        else:
            flash('用户名或密码错误。', 'danger')
            return redirect(url_for('auth.login'))
    else:
        flash('用户名或密码错误。', 'danger')
        return redirect(url_for('auth.login'))


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('您已退出登录。', 'success')
    # 退出后通常还是回首页，或者回登录页，看你喜好。这里回登录页可能更符合纯后台系统。
    return redirect(url_for('auth.login'))