import pymysql
import traceback
from werkzeug.security import generate_password_hash

print("="*60)
print("默认管理员创建脚本")
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

# 默认管理员信息
DEFAULT_ADMIN = {
    'username': 'admin',
    'email': 'admin@example.com',
    'password': 'admin123'
}

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
    
    # 检查管理员表是否存在
    cursor.execute("SHOW TABLES LIKE 'admin_users'")
    if not cursor.fetchone():
        print("\n× 管理员表不存在，请先创建表")
        conn.close()
        exit(1)
    
    # 检查默认管理员是否已存在
    cursor.execute("SELECT COUNT(*) FROM admin_users WHERE username = %s", (DEFAULT_ADMIN['username'],))
    admin_count = cursor.fetchone()[0]
    
    if admin_count > 0:
        print(f"\n! 默认管理员 '{DEFAULT_ADMIN['username']}' 已存在")
        
        # 显示管理员信息
        cursor.execute("SELECT * FROM admin_users WHERE username = %s", (DEFAULT_ADMIN['username'],))
        admin = cursor.fetchone()
        print("\n现有管理员信息:")
        print(f"  • ID: {admin[0]}")
        print(f"  • 用户名: {admin[1]}")
        print(f"  • 邮箱: {admin[2]}")
        print(f"  • 状态: {admin[4]}")
        print(f"  • 创建时间: {admin[5]}")
        
        # 询问是否要更新管理员
        update = input("\n是否更新此管理员的密码? (y/n): ")
        if update.lower() == 'y':
            # 生成新密码哈希
            password_hash = generate_password_hash(DEFAULT_ADMIN['password'])
            
            # 更新管理员密码
            cursor.execute(
                "UPDATE admin_users SET password_hash = %s WHERE username = %s",
                (password_hash, DEFAULT_ADMIN['username'])
            )
            conn.commit()
            print(f"\n✓ 已更新管理员 '{DEFAULT_ADMIN['username']}' 的密码")
    else:
        print(f"\n正在创建默认管理员...")
        
        # 生成密码哈希
        password_hash = generate_password_hash(DEFAULT_ADMIN['password'])
        
        # 插入管理员
        cursor.execute(
            "INSERT INTO admin_users (username, email, password_hash) VALUES (%s, %s, %s)",
            (DEFAULT_ADMIN['username'], DEFAULT_ADMIN['email'], password_hash)
        )
        conn.commit()
        print(f"\n✓ 管理员 '{DEFAULT_ADMIN['username']}' 创建成功")
    
    # 列出所有管理员
    cursor.execute("SELECT * FROM admin_users")
    admins = cursor.fetchall()
    
    print("\n所有管理员列表:")
    for admin in admins:
        print(f"  • ID: {admin[0]}")
        print(f"  • 用户名: {admin[1]}")
        print(f"  • 邮箱: {admin[2]}")
        print(f"  • 状态: {admin[4]}")
        print(f"  • 创建时间: {admin[5]}")
        print("")
    
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