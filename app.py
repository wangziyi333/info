from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'test_key_123456')

# ===================== 【 Render 专用数据库】 =====================
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///online_check.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "connect_args": {"check_same_thread": False}
}
db = SQLAlchemy(app)

# ======================== 模型 =============================
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

class Log(db.Model):
    __tablename__ = 'log'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(200), nullable=False)
    operator = db.Column(db.String(50), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)

# ===================== 健康检查 =====================
@app.route('/health')
def health():
    return "ok", 200

# ===================== 路由 =====================
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
            flash('用户名或密码错误')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    try:
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user:
            session.clear()
            return redirect(url_for('login'))
        return render_template('profile.html', user=user)
    except:
        return redirect(url_for('login'))

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    try:
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if request.method == 'POST':
            user.name = request.form.get('name')
            user.department = request.form.get('department')
            user.position = request.form.get('position')
            db.session.commit()
            flash('修改成功')
            return redirect(url_for('profile'))
        return render_template('edit.html', user=user)
    except:
        return redirect(url_for('profile'))

# ===================== 初始化数据库 =====================
@app.route('/init_db')
def init_db():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', password='admin', name='管理员',
                         department='管理', position='管理员', entry_date=date(2020,1,1),
                         work_years=5, seniority_salary=1000, role='admin', status='approved')
            db.session.add(admin)
        db.session.commit()
    return "✅ 初始化成功！账号 admin / admin"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))