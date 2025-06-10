import pymysql
import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量（如果有）
load_dotenv()

# 数据库连接参数
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', '39.105.26.212'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'user': os.environ.get('DB_USER', 'museumdb'),
    'password': os.environ.get('DB_PASSWORD', '123456'),
    'database': os.environ.get('DB_NAME', 'museumdb'),
    'charset': 'utf8mb4'
}

def create_tables():
    """从SQL文件创建表"""
    try:
        # 读取SQL文件
        with open('create_tables.sql', 'r', encoding='utf-8') as file:
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
        print("✓ 表创建成功!")
        
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
        print(f"× 创建表失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("===== 开始创建用户表 =====")
    create_tables() 