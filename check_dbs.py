# test_db.py
import pymysql

# 请你只修改这 4 行！
MYSQL_HOST = 'localhost'
MYSQL_PORT = 3306
MYSQL_USER = 'root'
MYSQL_PASSWORD = '123456'  # 这里必须写对
MYSQL_DB = 'online_check'          # 必须是已存在的库

try:
    conn = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        charset='utf8'
    )
    print("✅ 数据库连接成功！")
    conn.close()
except Exception as e:
    print("❌ 连接失败：", e)