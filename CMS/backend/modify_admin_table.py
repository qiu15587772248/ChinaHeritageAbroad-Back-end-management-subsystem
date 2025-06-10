import pymysql
import traceback

# --- 数据库连接配置 ---
DB_CONFIG = {
    'host': '39.105.26.212',
    'port': 3306,
    'user': 'museumdb',
    'password': '123456', # 请确保这是正确的数据库密码
    'database': 'museumdb',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor # 使用 DictCursor 更方便地处理列名
}

# --- 要更新的管理员用户名和新密码 ---
ADMIN_USERNAME_TO_UPDATE = 'admin'
NEW_PLAINTEXT_PASSWORD = '123456'

def modify_admin_users_table():
    conn = None
    try:
        print(f"正在连接到MySQL数据库: {DB_CONFIG['database']}@{DB_CONFIG['host']}...")
        conn = pymysql.connect(**DB_CONFIG)
        print("✓ 数据库连接成功!")
        
        with conn.cursor() as cursor:
            # 1. 尝试删除 password_hash 列
            try:
                print(f"正在尝试删除 'admin_users' 表中的 'password_hash' 列...")
                cursor.execute("ALTER TABLE admin_users DROP COLUMN password_hash")
                print("✓ 'password_hash' 列已成功删除 (或之前不存在)。")
            except pymysql.err.OperationalError as e:
                if e.args[0] == 1091: # Can't DROP 'password_hash'; check that column/key exists
                    print("ℹ️ 'password_hash' 列不存在，无需删除。")
                else:
                    raise # 重新抛出其他类型的 OperationalError

            # 2. 尝试添加 password 列
            try:
                print(f"正在尝试向 'admin_users' 表中添加 'password' 列 (VARCHAR(255) NOT NULL)...")
                cursor.execute("ALTER TABLE admin_users ADD COLUMN password VARCHAR(255) NOT NULL")
                print("✓ 'password' 列已成功添加。")
            except pymysql.err.OperationalError as e:
                if e.args[0] == 1060: # Duplicate column name 'password'
                    print("ℹ️ 'password' 列已存在，无需添加。")
                else:
                    raise # 重新抛出其他类型的 OperationalError

            # 3. 更新 admin 用户的密码
            print(f"正在更新用户 '{ADMIN_USERNAME_TO_UPDATE}' 的密码为 '{NEW_PLAINTEXT_PASSWORD}'...")
            sql_update_password = "UPDATE admin_users SET password = %s WHERE username = %s"
            rows_affected = cursor.execute(sql_update_password, (NEW_PLAINTEXT_PASSWORD, ADMIN_USERNAME_TO_UPDATE))
            
            if rows_affected > 0:
                print(f"✓ 用户 '{ADMIN_USERNAME_TO_UPDATE}' 的密码已成功更新为 '{NEW_PLAINTEXT_PASSWORD}'。")
            else:
                print(f"⚠️ 未找到用户名为 '{ADMIN_USERNAME_TO_UPDATE}' 的记录，密码未更新。请检查用户名是否正确。")
                
            conn.commit()
            print("✓ 更改已提交。")

    except pymysql.MySQLError as e:
        print(f"数据库操作失败: {e}")
        traceback.print_exc()
        if conn:
            conn.rollback()
            print("❌ 操作已回滚。")
    except Exception as e:
        print(f"发生未知错误: {e}")
        traceback.print_exc()
        if conn:
            conn.rollback()
            print("❌ 操作已回滚。")
    finally:
        if conn and conn.open:
            conn.close()
            print("数据库连接已关闭。")

if __name__ == '__main__':
    print("="*60)
    print("开始修改 'admin_users' 表结构并更新管理员密码...")
    print("="*60)
    modify_admin_users_table()
    print("="*60)
    print("脚本执行完毕。")
    print("="*60) 