import pymysql
import traceback

print("="*60)
print("管理员用户表创建脚本")
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

# 创建admin_users表的SQL语句
CREATE_ADMIN_USERS = """
CREATE TABLE IF NOT EXISTS admin_users (
  userid INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  email VARCHAR(100),
  password_hash VARCHAR(255) NOT NULL,
  status VARCHAR(20) DEFAULT 'active',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  last_login DATETIME
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

CREATE_INDEX = "CREATE INDEX idx_admin_username ON admin_users(username);"

try:
    print(f"正在连接到MySQL服务器...")
    print(f"主机: {DB_CONFIG['host']}")
    print(f"用户: {DB_CONFIG['user']}")
    print(f"数据库: {DB_CONFIG['database']}")
    
    # 连接数据库
    conn = pymysql.connect(**DB_CONFIG)
    print("✓ 数据库连接成功!")
    
    # 创建游标
    cursor = conn.cursor()
    
    # 检查管理员用户表是否已存在
    cursor.execute("SHOW TABLES LIKE 'admin_users'")
    if cursor.fetchone():
        print("! 管理员用户表已存在")
        
        # 查看现有表结构
        cursor.execute("DESCRIBE admin_users")
        columns = cursor.fetchall()
        
        print("\n管理员用户表结构:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]}")
            
        # 询问是否要删除现有表重新创建
        recreate = input("\n是否删除现有表并重新创建? (y/n): ")
        if recreate.lower() == 'y':
            print("\n正在删除现有表...")
            cursor.execute("DROP TABLE admin_users")
            print("✓ 现有表已删除")
        else:
            print("\n保留现有表，操作已取消")
            conn.close()
            print("\n数据库连接已关闭")
            print("\n" + "="*60)
            print("脚本结束")
            print("="*60)
            exit()
    
    # 创建表
    print("\n正在创建管理员用户表...")
    cursor.execute(CREATE_ADMIN_USERS)
    print("✓ 管理员用户表创建成功!")
    
    # 创建索引
    try:
        print("\n正在创建索引...")
        cursor.execute(CREATE_INDEX)
        print("✓ 索引创建成功!")
    except Exception as e:
        print(f"! 索引创建失败: {e}")
        print("  可能是因为索引已存在")
        
        # 尝试捕获重复索引错误
        if "Duplicate" in str(e):
            print("! 索引已存在，跳过创建")
        else:
            print(f"× 创建索引时出错: {e}")
    
    # 提交更改
    conn.commit()
    
    # 验证表创建是否成功
    print("\n验证表创建...")
    cursor.execute("DESCRIBE admin_users")
    columns = cursor.fetchall()
    
    print("\n管理员用户表结构:")
    for col in columns:
        print(f"  - {col[0]}: {col[1]}")
    
    print("\n✓ 表创建和验证完成!")
    
    # 关闭连接
    cursor.close()
    conn.close()
    print("\n数据库连接已关闭")
    
except Exception as e:
    print(f"\n× 操作失败: {e}")
    traceback.print_exc()

print("\n" + "="*60)
print("脚本结束")
print("="*60) 