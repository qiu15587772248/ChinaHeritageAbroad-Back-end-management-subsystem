from app import db
from datetime import datetime

class AdminUser(db.Model):
    """后台管理员用户模型"""
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100))
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    role = db.Column(db.String(50), nullable=False, default='admin') # e.g., 'admin', 'super_admin'

    def __repr__(self):
        return f'<AdminUser {self.username} ({self.role})>'

    def verify_password(self, password_to_check):
        return self.password == password_to_check

    # The old has_permission can be removed or adapted if specific fine-grained permissions are needed beyond roles.
    # For now, role checks will be done in routes or via a role-specific decorator.


class CloudUser:
    """云端用户模型（用于访问云服务器上的移动端用户数据）"""
    
    @staticmethod
    def get_mobile_users(conn):
        """获取移动端用户列表 (包括status)"""
        with conn.cursor() as cursor:
            # 确保查询所有需要的字段，包括新的 status
            cursor.execute("SELECT userid, username, email, avatar, registration_time, last_login, status FROM mobile_users")
            return cursor.fetchall()
    
    @staticmethod
    def get_user(conn, user_id):
        """获取特定用户信息 (包括status)"""
        with conn.cursor() as cursor:
            cursor.execute("SELECT userid, username, email, avatar, registration_time, last_login, status FROM mobile_users WHERE userid = %s", (user_id,))
            return cursor.fetchone()
    
    @staticmethod
    def get_user_by_username(conn, username):
        """根据用户名获取用户信息 (包括status)"""
        with conn.cursor() as cursor:
            cursor.execute("SELECT userid, username, email, avatar, registration_time, last_login, status FROM mobile_users WHERE username = %s", (username,))
            return cursor.fetchone()
    
    @staticmethod
    def update_user(conn, user_id, data):
        """更新用户信息"""
        set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
        values = list(data.values())
        values.append(user_id)
        
        with conn.cursor() as cursor:
            sql = f"UPDATE mobile_users SET {set_clause} WHERE userid = %s"
            cursor.execute(sql, values)
        conn.commit()
    
    @staticmethod
    def delete_user(conn, user_id):
        """删除用户"""
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM mobile_users WHERE userid = %s", (user_id,))
        conn.commit()
    
    @staticmethod
    def create_user(conn, user_data):
        """创建新用户"""
        columns = ", ".join(user_data.keys())
        placeholders = ", ".join(["%s"] * len(user_data))
        values = list(user_data.values())
        
        with conn.cursor() as cursor:
            sql = f"INSERT INTO mobile_users ({columns}) VALUES ({placeholders})"
            cursor.execute(sql, values)
        conn.commit()
        
        # 返回新创建的用户ID
        with conn.cursor() as cursor:
            cursor.execute("SELECT LAST_INSERT_ID()")
            return cursor.fetchone()[0]


class WebUser:
    """知识服务子系统（Web端）用户模型 - 已更新以匹配实际表结构 (id 作为主键)"""
    
    @staticmethod
    def get_web_users(conn):
        """获取Web端用户列表 (字段已更新, 使用 id)"""
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, username, email, avatar, registration_time, last_login, status FROM web_users")
            return cursor.fetchall()
    
    @staticmethod
    def get_user(conn, user_id): # 参数名 user_id 保持，但对应数据库的 id 列
        """获取特定Web用户信息 (字段已更新, 使用 id)"""
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, username, email, avatar, registration_time, last_login, status FROM web_users WHERE id = %s", (user_id,))
            return cursor.fetchone()
    
    @staticmethod
    def get_user_by_username(conn, username):
        """根据用户名获取Web用户信息 (原get_user_by_name, 字段已更新, 使用 id)"""
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, username, email, avatar, registration_time, last_login, status FROM web_users WHERE username = %s", (username,))
            return cursor.fetchone()
    
    @staticmethod
    def update_user(conn, user_id, data): # 参数名 user_id 保持，但对应数据库的 id 列
        """更新Web用户信息 (字段已更新, 使用 id)"""
        set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
        values = list(data.values())
        values.append(user_id)
        
        with conn.cursor() as cursor:
            sql = f"UPDATE web_users SET {set_clause} WHERE id = %s"
            cursor.execute(sql, values)
        conn.commit()
    
    @staticmethod
    def delete_user(conn, user_id): # 参数名 user_id 保持，但对应数据库的 id 列
        """删除Web用户 (使用id)"""
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM web_users WHERE id = %s", (user_id,))
        conn.commit()
    
    @staticmethod
    def create_user(conn, user_data):
        """创建新Web用户 (字段已更新, 返回的id是自增主键)"""
        columns = ", ".join(user_data.keys())
        placeholders = ", ".join(["%s"] * len(user_data))
        values = list(user_data.values())
        
        with conn.cursor() as cursor:
            sql = f"INSERT INTO web_users ({columns}) VALUES ({placeholders})"
            cursor.execute(sql, values)
        conn.commit()
        
        # 返回新创建的用户ID (id)
        with conn.cursor() as cursor:
            cursor.execute("SELECT LAST_INSERT_ID()")
            return cursor.fetchone()[0]


# 注意：这个模型在迁移到云端后可能不再需要
class User(db.Model):
    """系统用户模型（该模型仅用于本地操作，实际数据来自云服务器）"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # 'admin', 'mobile', 'knowledge'
    email = db.Column(db.String(100))
    status = db.Column(db.String(20), default='active')  # 'active', 'disabled'
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_login = db.Column(db.DateTime)
    
    @staticmethod
    def sync_from_cloud(cloud_users, user_type):
        """从云端同步用户数据"""
        # 在实际应用中，这里会从云端API或数据库获取数据并同步
        # 这里只是一个示例
        pass 