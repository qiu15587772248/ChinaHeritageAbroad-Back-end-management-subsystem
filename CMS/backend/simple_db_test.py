import pymysql
import traceback
from werkzeug.security import check_password_hash, generate_password_hash

print("="*60)
print("MySQL数据库连接测试脚本")
print("="*60)

# 数据库连接参数
DB_CONFIG = {
    'host': '39.105.26.212',
    'port': 3306,
    'user': 'museumdb',
    'password': '123456',
    'database': 'museumdb',
    'charset': 'utf8mb4'
}

try:
    print(f"正在连接到MySQL服务器...")
    print(f"主机: {DB_CONFIG['host']}")
    print(f"端口: {DB_CONFIG['port']}")
    print(f"用户: {DB_CONFIG['user']}")
    print(f"数据库: {DB_CONFIG['database']}")
    
    # 尝试连接
    conn = pymysql.connect(**DB_CONFIG)
    
    print("\n✓ 数据库连接成功!")
    
    # 测试基本查询
    with conn.cursor() as cursor:
        # 获取服务器版本
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"\nMySQL版本: {version[0]}")
        
        # 获取当前数据库
        cursor.execute("SELECT DATABASE()")
        db = cursor.fetchone()
        print(f"当前数据库: {db[0]}")
        
        # 列出所有表
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        if tables:
            print("\n数据库中的表:")
            for table in tables:
                print(f"  - {table[0]}")
        else:
            print("\n当前数据库中没有表")
            
    # 关闭连接
    conn.close()
    print("\n数据库连接已关闭")

except Exception as e:
    print(f"\n× 连接失败: {e}")
    traceback.print_exc()

print("\n" + "="*60)
print("测试完成")
print("="*60)

