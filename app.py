from flask import Flask, render_template, request, redirect, url_for, flash, session
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'test_key_123456')

# ===================== 内存用户数据（Render 100% 可用） =====================
users = [
    {"id": 1, "username": "admin", "password": "admin", "name": "系统管理员",
     "department": "管理部", "position": "管理员", "entry_date": "2020-01-01",
     "work_years": 5, "seniority_salary": 1000, "role": "admin", "status": "approved"}
]

# ===================== 健康检查 =====================
@app.route('/health')
def health():
    return "ok", 200

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
        
        user = None
        for u in users:
            if u['username'] == username and u['password'] == password:
                user = u
                break
        
        if user:
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['name'] = user['name']
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
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = None
    for u in users:
        if u['id'] == session['user_id']:
            user = u
            break
    
    if not user:
        session.clear()
        return redirect(url_for('login'))
    
    return render_template('profile.html', user=user)

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = None
    for u in users:
        if u['id'] == session['user_id']:
            user = u
            break
    
    return render_template('edit.html', user=user)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))