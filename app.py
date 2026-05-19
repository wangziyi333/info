from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import pymysql

pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.secret_key = 'your_secret_key_here_change_in_production'

# 你的 MySQL 配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost:3306/online_check?charset=utf8'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    entry_date = db.Column(db.Date, nullable=False)
    work_years = db.Column(db.Integer, default=0)
    seniority_salary = db.Column(db.Numeric(10, 2), default=0.00)
    role = db.Column(db.String(20), default='user')
    status = db.Column(db.String(20), default='pending')
    reject_reason = db.Column(db.String(500), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'department': self.department,
            'position': self.position,
            'entry_date': self.entry_date.strftime('%Y-%m-%d') if self.entry_date else '',
            'work_years': self.work_years,
            'seniority_salary': str(self.seniority_salary),
            'role': self.role,
            'status': self.status,
            'reject_reason': self.reject_reason
        }


class Log(db.Model):
    __tablename__ = 'log'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(200), nullable=False)
    operator = db.Column(db.String(50), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)


@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('profile'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['role'] = user.role
            session['name'] = user.name
            return redirect(url_for('profile'))
        else:
            flash('用户名或密码错误', 'error')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('logout'))
    return render_template('profile.html', user=user)


# ===================== 【已升级】支持手动修改 工龄 + 工龄工资 =====================
@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('logout'))

    if user.status == 'approved':
        flash('您的信息已审核通过，无法修改', 'error')
        return redirect(url_for('profile'))

    if request.method == 'POST':
        user.name = request.form.get('name')
        user.department = request.form.get('department')
        user.position = request.form.get('position')
        entry_date_str = request.form.get('entry_date')
        if entry_date_str:
            user.entry_date = datetime.strptime(entry_date_str, '%Y-%m-%d').date()

        # ===================== 【新增功能】手动修改工龄和工龄工资 =====================
        work_years = request.form.get('work_years')
        if work_years:
            user.work_years = int(work_years)

        seniority_salary = request.form.get('seniority_salary')
        if seniority_salary:
            user.seniority_salary = float(seniority_salary)
        # ==============================================================================

        if user.status == 'rejected':
            user.status = 'submitted'
        else:
            user.status = 'pending'

        user.reject_reason = None
        db.session.commit()

        log = Log(user_id=user.id, action='员工修改个人信息（含工龄/工龄工资）', operator=user.name)
        db.session.add(log)
        db.session.commit()

        flash('信息修改成功（工龄/工龄工资已更新）', 'success')
        return redirect(url_for('profile'))

    return render_template('edit.html', user=user)


@app.route('/confirm')
def confirm():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('logout'))
    if user.status != 'pending':
        flash('当前状态无法确认', 'error')
        return redirect(url_for('profile'))

    user.status = 'submitted'
    user.reject_reason = None
    db.session.commit()

    log = Log(user_id=user.id, action='员工确认信息并提交审核', operator=user.name)
    db.session.add(log)
    db.session.commit()

    flash('信息已提交，请等待管理员审核', 'success')
    return redirect(url_for('profile'))


@app.route('/audit_list')
def audit_list():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session.get('role') != 'admin':
        return render_template('no_permission.html')

    status_filter = request.args.get('status', 'all')
    query = User.query
    if status_filter == 'pending':
        query = query.filter_by(status='pending')
    elif status_filter == 'submitted':
        query = query.filter_by(status='submitted')
    elif status_filter == 'approved':
        query = query.filter_by(status='approved')
    elif status_filter == 'rejected':
        query = query.filter_by(status='rejected')

    users = query.all()
    return render_template('audit_list.html', users=users, current_filter=status_filter)

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session.get('role') != 'admin':
        return render_template('no_permission.html')

    if request.method == 'POST':
        # 获取表单数据
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        department = request.form.get('department')
        position = request.form.get('position')
        entry_date_str = request.form.get('entry_date')
        work_years = int(request.form.get('work_years', 0))
        seniority_salary = float(request.form.get('seniority_salary', 0))

        # 判断账号是否已存在
        exist = User.query.filter_by(username=username).first()
        if exist:
            flash('用户名已存在', 'error')
            return redirect(url_for('add_user'))

        # 转换日期
        entry_date = datetime.strptime(entry_date_str, '%Y-%m-%d').date()

        # 创建新用户
        new_user = User(
            username=username,
            password=password,
            name=name,
            department=department,
            position=position,
            entry_date=entry_date,
            work_years=work_years,
            seniority_salary=seniority_salary,
            role='user',
            status='pending'
        )
        db.session.add(new_user)
        db.session.commit()

        # 记录日志
        operator = User.query.get(session['user_id'])
        log = Log(
            user_id=new_user.id,
            action='管理员新增员工账号',
            operator=operator.name if operator else 'admin'
        )
        db.session.add(log)
        db.session.commit()

        flash('添加员工成功！', 'success')
        return redirect(url_for('audit_list'))

    return render_template('add_user.html')

@app.route('/approve/<int:user_id>')
def approve(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session.get('role') != 'admin':
        return render_template('no_permission.html')
    user = User.query.get(user_id)
    if user:
        user.status = 'approved'
        user.reject_reason = None
        db.session.commit()

        operator = User.query.get(session['user_id'])
        log = Log(user_id=user.id, action='管理员审核通过', operator=operator.name if operator else 'admin')
        db.session.add(log)
        db.session.commit()

        flash(f'员工 {user.name} 审核通过', 'success')
    return redirect(url_for('audit_list'))


@app.route('/reject/<int:user_id>', methods=['GET', 'POST'])
def reject(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session.get('role') != 'admin':
        return render_template('no_permission.html')
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for('audit_list'))

    if request.method == 'POST':
        reason = request.form.get('reason', '').strip()
        if not reason:
            flash('请填写驳回原因', 'error')
            return redirect(url_for('reject', user_id=user_id))

        user.status = 'rejected'
        user.reject_reason = reason
        db.session.commit()

        operator = User.query.get(session['user_id'])
        log = Log(user_id=user.id, action=f'驳回：{reason}', operator=operator.name if operator else 'admin')
        db.session.add(log)
        db.session.commit()

        flash(f'员工 {user.name} 已驳回', 'success')
        return redirect(url_for('audit_list'))

    return render_template('reject.html', user=user)


@app.route('/reaudit/<int:user_id>')
def reaudit(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session.get('role') != 'admin':
        return render_template('no_permission.html')
    user = User.query.get(user_id)
    if user:
        user.status = 'pending'
        user.reject_reason = None
        db.session.commit()

        operator = User.query.get(session['user_id'])
        log = Log(user_id=user.id, action='管理员打回待审核', operator=operator.name if operator else 'admin')
        db.session.add(log)
        db.session.commit()

        flash(f'员工 {user.name} 已打回待审核', 'success')
    return redirect(url_for('audit_list'))


@app.route('/init_db')
def init_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', password='admin', name='系统管理员', department='管理部', position='管理员',
                         entry_date=date(2020, 1, 1), work_years=4, seniority_salary=800, role='admin',
                         status='approved')
            db.session.add(admin)
        if not User.query.filter_by(username='user01').first():
            u = User(username='user01', password='123456', name='张三', department='技术部', position='工程师',
                     entry_date=date(2022, 6, 15), work_years=2, seniority_salary=400, role='user', status='pending')
            db.session.add(u)
        db.session.commit()
    return '初始化成功'


if __name__ == '__main__':
    app.run(debug=True)