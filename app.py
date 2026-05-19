from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import os

app = Flask(__name__)
app.secret_key = "test_key_123456"

#  Render 免费版能用的数据库（不写文件，不会 500）
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/online_check.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "connect_args": {"check_same_thread": False}
}
db = SQLAlchemy(app)

# 模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(50))
    department = db.Column(db.String(50))
    position = db.Column(db.String(50))
    entry_date = db.Column(db.Date)
    work_years = db.Column(db.Integer)
    seniority_salary = db.Column(db.Numeric(10,2))
    role = db.Column(db.String(20))
    status = db.Column(db.String(20))
    reject_reason = db.Column(db.String(500))

# 健康检查
@app.route('/health')
def health():
    return "ok", 200

# 首页
@app.route('/')
def index():
    return redirect(url_for('login'))

# 登录
@app.route('/login', methods=['GET','POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.query.filter_by(username=username, password=password).first()
            if user:
                session['user_id'] = user.id
                return redirect(url_for('profile'))
        return render_template('login.html')
    except:
        return "正在初始化，请访问 /init_db"

# 个人页
@app.route('/profile')
def profile():
    try:
        user = User.query.first()
        return render_template('profile.html', user=user)
    except:
        return redirect(url_for('login'))

# 初始化数据库
@app.route('/init_db')
def init_db():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            u = User(
                username="admin",
                password="admin",
                name="管理员",
                department="管理部",
                position="管理员",
                entry_date=date(2020,1,1),
                work_years=5,
                seniority_salary=1000,
                role="admin",
                status="approved"
            )
            db.session.add(u)
            db.session.commit()
    return "✅ 初始化成功！去登录：admin / admin"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))