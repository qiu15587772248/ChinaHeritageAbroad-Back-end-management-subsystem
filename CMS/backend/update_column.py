import pymysql
import os

# 禁用.env文件加载
os.environ['FLASK_SKIP_DOTENV'] = '1'

# 数据库连接参数
DB_CONFIG = {
    'host': '39.105.26.212',
    'port': 3306,
    'user': 'museumdb',
    'password': '123456',
    'database': 'museumdb',
    'charset': 'utf8mb4'
}

def update_admin_table():
    """更新admin_users表结构"""
    try:
        # 连接数据库
        print(f"正在连接到数据库: {DB_CONFIG['host']}:{DB_CONFIG['port']} ({DB_CONFIG['database']})")
        conn = pymysql.connect(**DB_CONFIG)
        
        # 执行SQL脚本
        sql = "ALTER TABLE admin_users CHANGE COLUMN userid id INT(11) NOT NULL AUTO_INCREMENT;"
        
        with conn.cursor() as cursor:
            cursor.execute(sql)
            print(f"执行SQL: {sql}")
        
        conn.commit()
        print("✓ 表结构更新成功!")
        conn.close()
        return True
        
    except Exception as e:
        print(f"× 更新表结构失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("===== 开始更新admin_users表结构 =====")
    update_admin_table() 