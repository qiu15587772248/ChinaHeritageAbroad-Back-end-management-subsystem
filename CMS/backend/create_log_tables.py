import pymysql
import os
from dotenv import load_dotenv

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

def create_log_tables():
    """从SQL文件创建操作日志表"""
    try:
        # 读取SQL文件
        with open('create_log_tables.sql', 'r', encoding='utf-8') as file:
            sql_script = file.read()
        
        # 连接数据库
        print(f"正在连接到数据库: {DB_CONFIG['host']}:{DB_CONFIG['port']} ({DB_CONFIG['database']})")
        conn = pymysql.connect(**DB_CONFIG)
        
        # 执行SQL脚本
        with conn.cursor() as cursor:
            # 分割SQL语句并执行
            for statement in sql_script.split(';'):
                if statement.strip():
                    cursor.execute(statement)
                    print(f"执行SQL: {statement.strip()[:50]}...")
        
        conn.commit()
        print("✓ 操作日志表创建成功!")
        
        # 验证表是否已创建
        with conn.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print("\n数据库中的表:")
            for table in tables:
                table_name = list(table.values())[0] if isinstance(table, dict) else table[0]
                print(f"  - {table_name}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"× 创建操作日志表失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("===== 开始创建操作日志表 =====")
    create_log_tables() 