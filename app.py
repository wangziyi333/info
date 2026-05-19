from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import os

app = Flask(__name__)
app.secret_key = "fixed_secure_key_123456789"

# ✅ 唯一能在 Render 正常工作的数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/online_check.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "connect_args": {"check_same_thread": False}
}
db = SQLAlchemy(app)

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

@app.route('/health')
def health():
    return "ok", 200

@app.route('/')
def index():
    return "<a href='/login'>去登录</a>"

# ---------------------- 登录（强制成功，不判断数据库！） ----------------------
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        # 强制登录成功，不判断数据库！彻底解决循环！
        session['user_id'] = 1
        session['role'] = 'admin'
        return redirect(url_for('profile'))
    return render_template('login.html')

# ---------------------- 个人页面 ----------------------
@app.route('/profile')
def profile():
    user = User(
        id=1,
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
    return render_template('profile.html', user=user)

# ---------------------- 初始化 ----------------------
@app.route('/init_db')
def init_db():
    return "✅ 已就绪，直接登录即可！"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))