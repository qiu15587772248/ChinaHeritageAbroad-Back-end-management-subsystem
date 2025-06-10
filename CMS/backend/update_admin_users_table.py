import pymysql
from pymysql.cursors import DictCursor

# --- 数据库连接配置 ---
DB_HOST = '39.105.26.212'
DB_PORT = 3306  # 默认MySQL端口
DB_USER = 'museumdb'
DB_PASSWORD = '123456' # 请确保这是最新的密码
DB_NAME = 'museumdb'
# --- END ---

def execute_sql(connection, sql, values=None):
    """执行SQL语句"""
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, values)
        connection.commit()
        print(f"Successfully executed: {sql}")
    except Exception as e:
        print(f"Error executing {sql}: {e}")
        connection.rollback()

def main():
    conn = None
    try:
        # 连接数据库
        conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4',
            cursorclass=DictCursor
        )
        print("Successfully connected to the database.")

        # 1. 检查并添加 role 列
        add_role_column_sql = """
        ALTER TABLE admin_users
        ADD COLUMN role VARCHAR(50) NOT NULL DEFAULT 'admin' COMMENT '用户角色: admin, super_admin'
        """
        print("\nAttempting to add 'role' column to 'admin_users' table...")
        column_exists = False
        try:
            with conn.cursor() as cursor:
                cursor.execute("SHOW COLUMNS FROM admin_users LIKE 'role'")
                result = cursor.fetchone()
                if result:
                    column_exists = True
                    print("'role' column already exists in 'admin_users' table.")
        except Exception as e:
            print(f"Error checking 'role' column: {e}")
            return # 如果检查列时出错，则不继续

        if not column_exists:
            execute_sql(conn, add_role_column_sql)
        else:
            # 如果列已存在，可以考虑更新列的定义，例如注释
            try:
                 with conn.cursor() as cursor:
                    cursor.execute("ALTER TABLE admin_users MODIFY COLUMN role VARCHAR(50) NOT NULL DEFAULT 'admin' COMMENT '用户角色: admin, super_admin'")
                 conn.commit()
                 print("Ensured 'role' column definition is up-to-date.")
            except Exception as e:
                 print(f"Could not update 'role' column definition (this might be okay if definition is already correct): {e}")


        # 2. 将用户名为 'admin' 的用户角色设置为 'super_admin'
        # 您可以根据需要修改或添加更多用户的角色更新
        update_admin_role_sql = "UPDATE admin_users SET role = %s WHERE username = %s AND role != %s"
        print("\nAttempting to update 'admin' user role to 'super_admin'...")
        execute_sql(conn, update_admin_role_sql, ('super_admin', 'admin', 'super_admin'))
        
        # 您可以添加更多的更新语句来设置其他用户的角色
        # execute_sql(conn, update_admin_role_sql, ('super_admin', 'another_admin_username', 'super_admin'))

        print("\nDatabase update script finished.")

    except pymysql.Error as e:
        print(f"Database connection error: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == '__main__':
    main() 