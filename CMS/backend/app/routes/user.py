from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import AdminUser, CloudUser, WebUser
from app.models.log import OperationLog
import pymysql
import functools
from datetime import datetime
import json

user_bp = Blueprint('user', __name__)

# 创建数据库连接
def get_cloud_db_connection():
    return pymysql.connect(
        host=current_app.config['DB_HOST'],
        port=current_app.config['DB_PORT'],
        user=current_app.config['DB_USER'],
        password=current_app.config['DB_PASSWORD'],
        database=current_app.config['DB_NAME'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

# 新的基于角色的权限检查装饰器
def role_required(required_roles):
    """
    装饰器：检查当前登录用户是否具有所需的角色之一。
    `required_roles` 可以是单个角色字符串或角色列表。
    """
    def decorator(f):
        @functools.wraps(f)
        @jwt_required() # Ensure JWT is present and valid first
        def decorated_function(*args, **kwargs):
            identity = get_jwt_identity()
            # Ensure identity is a dictionary and contains 'id'
            if not isinstance(identity, dict) or 'id' not in identity:
                return jsonify(message="无效的令牌格式"), 401

            current_user = AdminUser.query.get(identity['id'])
            if not current_user:
                return jsonify(message="用户未找到或令牌无效"), 401
            
            user_role = getattr(current_user, 'role', None) 
            if not user_role:
                 return jsonify(message="用户角色未设置"), 403


            if isinstance(required_roles, str):
                allowed_roles_list = [required_roles]
            else:
                allowed_roles_list = required_roles
            
            if user_role not in allowed_roles_list:
                return jsonify(message="权限不足，需要以下角色之一: " + ", ".join(allowed_roles_list)), 403
            
            # 将当前用户对象传递给路由函数，方便使用
            kwargs['current_user_from_decorator'] = current_user
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# --- Admin User Routes ---

@user_bp.route('/admin', methods=['GET'])
@jwt_required() # 所有登录的管理员都可以查看列表
def get_admin_users(**kwargs): # current_user_from_decorator is not strictly needed here but good for consistency
    """获取管理员用户列表"""
    users = AdminUser.query.all()
    return jsonify({
        'users': [
            {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': getattr(user, 'role', 'admin'),
                'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else None,
                'last_login': user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else None
            } for user in users
        ]
    })


@user_bp.route('/admin', methods=['POST'])
@role_required('super_admin') 
def create_admin_user(current_user_from_decorator, **kwargs):
    """创建管理员用户 (仅限超级管理员)"""
    current_operator = current_user_from_decorator
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    role = data.get('role', 'admin') 
    
    if not username or not password:
        return jsonify({'message': '用户名和密码不能为空'}), 400
        
    if AdminUser.query.filter_by(username=username).first():
        return jsonify({'message': '用户名已存在'}), 400
    
    if role not in ['admin', 'super_admin']:
         return jsonify({'message': '无效的角色指定，只能是 "admin" 或 "super_admin"'}), 400

    new_user = AdminUser(
        username=username,
        email=email,
        role=role
    )
    new_user.password = password 
    
    db.session.add(new_user)
    db.session.commit()
    
    log = OperationLog(
        admin_id=current_operator.id,
        admin_username=current_operator.username,
        operation_type='用户管理',
        operation_content=f'创建管理员用户 {username} (角色: {role})',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'message': '管理员创建成功',
        'user': {
            'id': new_user.id, 
            'username': new_user.username, 
            'email': new_user.email, 
            'role': new_user.role
        }
    }), 201


@user_bp.route('/admin/<int:user_id>', methods=['PUT'])
@jwt_required() 
def update_admin_user(user_id, **kwargs):
    """更新管理员用户"""
    identity = get_jwt_identity()
    current_operator = AdminUser.query.get(identity['id']) # Get current_operator from JWT identity directly
    if not current_operator:
        return jsonify({'message': '操作用户未找到'}), 401

    user_to_update = AdminUser.query.get(user_id)
    if not user_to_update:
        return jsonify({'message': '目标用户不存在'}), 404

    # 权限检查
    can_edit = False
    if current_operator.role == 'super_admin':
        can_edit = True
    elif current_operator.role == 'admin' and current_operator.id == user_to_update.id:
        can_edit = True
    
    if not can_edit:
        return jsonify({'message': '权限不足以编辑此用户'}), 403

    data = request.get_json()
    log_details = []

    # 用户名通常不建议修改，如果需要，确保 super_admin 操作并处理唯一性
    # if 'username' in data and current_operator.role == 'super_admin':
    #     new_username = data['username']
    #     if new_username != user_to_update.username:
    #         existing_user = AdminUser.query.filter(AdminUser.username == new_username, AdminUser.id != user_to_update.id).first()
    #         if existing_user:
    #             return jsonify({'message': '该用户名已被其他用户使用'}), 400
    #         user_to_update.username = new_username
    #         log_details.append(f"用户名更改为: {new_username}")


    if 'email' in data:
        if user_to_update.email != data['email']:
            user_to_update.email = data['email']
            log_details.append(f"邮箱更改为: {data['email']}")
        
    if 'password' in data and data['password']: 
        user_to_update.password = data['password'] 
        log_details.append("密码已更新")
    
    if 'role' in data:
        if current_operator.role == 'super_admin':
            new_role = data['role']
            if new_role not in ['admin', 'super_admin']:
                return jsonify({'message': '无效的角色指定'}), 400
            
            # 防止最后一个 super_admin 降级自己
            if current_operator.id == user_to_update.id and user_to_update.role == 'super_admin' and new_role == 'admin':
                super_admin_count = AdminUser.query.filter_by(role='super_admin').count()
                if super_admin_count <= 1:
                    return jsonify({'message': '不能将最后一个超级管理员的角色降级'}), 403
            
            if user_to_update.role != new_role:
                user_to_update.role = new_role
                log_details.append(f"角色更改为: {new_role}")
        elif current_operator.id == user_to_update.id and user_to_update.role != data['role']:
            return jsonify({'message': '普通管理员不能修改自己的角色'}), 403
        elif current_operator.role == 'admin' and 'role' in data and user_to_update.role != data['role']:
             # 再次确认普通管理员不能修改他人角色，即使他们能编辑其他字段（理论上不应发生）
            return jsonify({'message': '普通管理员不能修改他人角色'}), 403


    if not log_details and not ('password' in data and data['password']): # No actual changes made
        return jsonify({
            'message': '未提供任何更改',
            'user': {
                'id': user_to_update.id, 
                'username': user_to_update.username, 
                'email': user_to_update.email, 
                'role': user_to_update.role
            }
        })

    db.session.commit()
    
    log_operation_content = f'更新管理员用户 {user_to_update.username} (ID: {user_to_update.id})。'
    if log_details:
        log_operation_content += " 详情: " + ", ".join(log_details) + "."
    else: # Only password might have been changed if log_details is empty
        log_operation_content += " (可能仅更新了密码或无实际数据更改)。"


    log = OperationLog(
        admin_id=current_operator.id,
        admin_username=current_operator.username,
        operation_type='用户管理',
        operation_content=log_operation_content,
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'message': '管理员信息更新成功',
        'user': {
            'id': user_to_update.id, 
            'username': user_to_update.username, 
            'email': user_to_update.email, 
            'role': user_to_update.role
        }
    })


@user_bp.route('/admin/<int:user_id>', methods=['DELETE'])
@role_required('super_admin') 
def delete_admin_user(user_id, current_user_from_decorator, **kwargs):
    """删除管理员用户 (仅限超级管理员)"""
    current_operator = current_user_from_decorator
    
    if user_id == current_operator.id:
        return jsonify({'message': '不能删除当前登录用户 (自己)'}), 400
    
    user_to_delete = AdminUser.query.get(user_id)
    if not user_to_delete:
        return jsonify({'message': '用户不存在'}), 404
    
    if user_to_delete.role == 'super_admin':
        super_admin_count = AdminUser.query.filter_by(role='super_admin').count()
        if super_admin_count <= 1:
            return jsonify({'message': '不能删除最后一个超级管理员'}), 403

    username_deleted = user_to_delete.username
    role_deleted = user_to_delete.role
    
    db.session.delete(user_to_delete)
    db.session.commit()
    
    log = OperationLog(
        admin_id=current_operator.id,
        admin_username=current_operator.username,
        operation_type='用户管理',
        operation_content=f'删除管理员用户 {username_deleted} (ID: {user_id}, 角色: {role_deleted})',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'message': '管理员删除成功'})

# --- Mobile User Routes ---
# Assuming both 'admin' and 'super_admin' can manage mobile and web users.
# Adjust roles if needed.

@user_bp.route('/mobile', methods=['GET'])
@role_required(['super_admin', 'admin'])
def get_mobile_users(current_user_from_decorator, **kwargs):
    """获取移动端用户列表 (已更新, 支持分页和过滤)"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        username_filter = request.args.get('username', '', type=str)
        status_filter = request.args.get('status', '', type=str)

        conn = get_cloud_db_connection()
        
        base_select = "SELECT userid, username, email, avatar, registration_time, last_login, status FROM mobile_users"
        count_select = "SELECT COUNT(*) as total FROM mobile_users"
        
        conditions = []
        params = []

        if username_filter:
            conditions.append("username LIKE %s")
            params.append(f"%{username_filter}%")
        if status_filter:
            conditions.append("status = %s")
            params.append(status_filter)

        where_clause = ""
        if conditions:
            where_clause = " WHERE " + " AND ".join(conditions)

        # Get total count with filters
        with conn.cursor() as cursor:
            cursor.execute(count_select + where_clause, tuple(params))
            total_count = cursor.fetchone()['total']
        
        # Get paginated data
        query_pagination = f" ORDER BY userid ASC LIMIT %s OFFSET %s" # Default order by userid ASC
        offset = (page - 1) * limit
        
        final_query = base_select + where_clause + query_pagination
        final_params = tuple(params + [limit, offset])

        with conn.cursor() as cursor:
            cursor.execute(final_query, final_params)
            users_page = cursor.fetchall()

        conn.close()
        
        for user in users_page:
            if user.get('avatar'):
                user['has_avatar'] = True
                user.pop('avatar')
            else:
                user['has_avatar'] = False
                if 'avatar' in user:
                    user.pop('avatar')
        
        return jsonify({'code': 20000, 'data': {'users': users_page, 'total': total_count}})
        
    except Exception as e:
        current_app.logger.error(f"Error fetching mobile users: {e}")
        return jsonify({'code': 50000, 'message': f'获取移动端用户列表失败: {str(e)}'}), 500


@user_bp.route('/mobile', methods=['POST'])
@role_required(['super_admin', 'admin'])
def create_mobile_user(current_user_from_decorator, **kwargs):
    """创建移动端用户 (已更新)"""
    current_operator = current_user_from_decorator
    data = request.get_json()
    
    required_fields = ['username', 'password'] 
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'code': 40000, 'message': f'{field}不能为空'}), 400
    
    try:
        conn = get_cloud_db_connection()
        
        existing_user = CloudUser.get_user_by_username(conn, data['username'])
        if existing_user:
            conn.close()
            return jsonify({'code': 40000, 'message': '用户名已存在'}), 400
        
        # Prepare user_data, ensure all fields for the table are considered
        user_data = {
            'username': data['username'],
            'password': data['password'], # Assuming plaintext for course design
            'email': data.get('email'), # Can be None
            'status': data.get('status', '正常') # Default to '正常'
            # 'avatar': data.get('avatar'), # Avatar might be handled by a separate upload endpoint
            # 'registration_time' is handled by DB default
        }
        # Filter out None values for optional fields if model's create_user expects only provided fields
        user_data_to_create = {k: v for k, v in user_data.items() if v is not None or k in required_fields}

        if user_data_to_create['status'] not in ['正常', '禁用']:
            conn.close()
            return jsonify({'code': 40000, 'message': '无效的用户状态值'}), 400

        new_user_id = CloudUser.create_user(conn, user_data_to_create)
        
        # Fetch the created user's full info for logging and response
        new_user_info = CloudUser.get_user(conn, new_user_id) if new_user_id else {"username": data['username'], "userid": new_user_id}
        conn.close()

        log = OperationLog(
            admin_id=current_operator.id,
            admin_username=current_operator.username,
            operation_type='用户管理',
            operation_content=f'创建移动端用户 {new_user_info.get("username", "N/A")} (ID: {new_user_id})',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({'code': 20000, 'message': '移动端用户创建成功', 'data': {'user': new_user_info}}), 201
        
    except Exception as e:
        current_app.logger.error(f"Error creating mobile user: {e}")
        if 'conn' in locals() and conn and conn.open: conn.close()
        return jsonify({'code': 50000, 'message': f'创建移动端用户失败: {str(e)}'}), 500


@user_bp.route('/mobile/<int:user_id>', methods=['PUT'])
@role_required(['super_admin', 'admin'])
def update_mobile_user(user_id, current_user_from_decorator, **kwargs):
    """更新移动端用户信息 (已更新)"""
    data = request.get_json() # Data from frontend e.g. {'status': '禁用'}
    
    if not data:
        return jsonify({'code': 40000, 'message': '请求数据不能为空'}), 400

    conn = None
    try:
        conn = get_cloud_db_connection()
        with conn.cursor() as cursor:
            # Fetch user to ensure it exists and to get username for logging
            cursor.execute("SELECT userid, username, avatar FROM mobile_users WHERE userid = %s", (user_id,))
            user_to_update_details = cursor.fetchone() 

            if not user_to_update_details:
                return jsonify({'code': 40400, 'message': '用户不存在'}), 404
            
            valid_fields_for_update = ['status', 'email'] 
            data_to_persist = {key: data[key] for key in data if key in valid_fields_for_update}

            if not data_to_persist:
                 return jsonify({'code': 40000, 'message': '没有有效的更新字段'}), 400

            CloudUser.update_user(conn, user_id, data_to_persist) 

        # Log operation
        try:
            log_changes_str = json.dumps(data_to_persist, ensure_ascii=False)
        except TypeError:
            log_changes_str = str(data_to_persist)

        username_for_log = user_to_update_details.get('username', f'ID {user_id}')
        
        operation_content = f'更新移动端用户 {username_for_log} (ID: {user_id})。更新内容: {log_changes_str}'

        log_entry = OperationLog(
            admin_id=current_user_from_decorator.id,
            admin_username=current_user_from_decorator.username,
            operation_type='用户管理', 
            operation_content=operation_content,
            ip_address=request.remote_addr
        )
        db.session.add(log_entry)
        db.session.commit()

        return jsonify({'code': 20000, 'message': '移动端用户信息更新成功'}), 200

    except pymysql.Error as db_err:
        current_app.logger.error(f"Database error during mobile user update or logging for user {user_id}: {db_err}")
        try:
            db.session.rollback()
        except Exception as rb_err_sqlalchemy:
            current_app.logger.error(f"Error during SQLAlchemy session rollback: {rb_err_sqlalchemy}")
        return jsonify({'code': 50000, 'message': f'数据库操作失败: {str(db_err)}'}), 500
    except Exception as e:
        error_message = str(e)
        error_type = type(e).__name__
        current_app.logger.error(f"Error during mobile user update for user_id {user_id}. Type: {error_type}, Message: {error_message}")
        
        import traceback
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")

        if conn and conn.open: 
            try:
                conn.rollback() 
            except Exception as rb_err_pymysql:
                current_app.logger.error(f"Error during PyMySQL connection rollback: {rb_err_pymysql}")
        try:
            db.session.rollback()
        except Exception as rb_err_sqlalchemy:
            current_app.logger.error(f"Error during SQLAlchemy session rollback: {rb_err_sqlalchemy}")
        
        return jsonify({'code': 50000, 'message': error_message}), 500
    finally:
        if conn and conn.open:
            conn.close()


@user_bp.route('/mobile/<int:user_id>', methods=['DELETE'])
@role_required(['super_admin', 'admin'])
def delete_mobile_user(user_id, current_user_from_decorator, **kwargs):
    """删除移动端用户"""
    current_operator = current_user_from_decorator
    try:
        conn = get_cloud_db_connection()
        
        user_to_delete = CloudUser.get_user(conn, user_id)
        if not user_to_delete:
            conn.close()
            return jsonify({'message': '移动端用户不存在'}), 404
            
        username_deleted = user_to_delete.get('username', 'N/A')
        CloudUser.delete_user(conn, user_id)
        conn.close()

        log = OperationLog(
            admin_id=current_operator.id,
            admin_username=current_operator.username,
            operation_type='用户管理',
            operation_content=f'删除移动端用户 {username_deleted} (ID: {user_id})',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({'message': '移动端用户删除成功'})
        
    except Exception as e:
        current_app.logger.error(f"Error deleting mobile user {user_id}: {e}")
        if 'conn' in locals() and conn: conn.close()
        return jsonify({'message': f'删除移动端用户失败: {str(e)}'}), 500

# --- Web User (Knowledge Service Subsystem) Routes ---

@user_bp.route('/web', methods=['GET'])
@role_required(['super_admin', 'admin'])
def get_web_users(current_user_from_decorator, **kwargs):
    """获取Web端用户列表 (已更新, 支持分页和过滤, 使用 id)"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        username_filter = request.args.get('username', '', type=str)
        status_filter = request.args.get('status', '', type=str)

        conn = get_cloud_db_connection()

        base_select = "SELECT id, username, email, avatar, registration_time, last_login, status FROM web_users"
        count_select = "SELECT COUNT(*) as total FROM web_users"
        
        conditions = []
        params = []

        if username_filter:
            conditions.append("username LIKE %s")
            params.append(f"%{username_filter}%")
        if status_filter:
            conditions.append("status = %s")
            params.append(status_filter)

        where_clause = ""
        if conditions:
            where_clause = " WHERE " + " AND ".join(conditions)

        with conn.cursor() as cursor:
            cursor.execute(count_select + where_clause, tuple(params))
            total_count = cursor.fetchone()['total']
        
        query_pagination = f" ORDER BY id ASC LIMIT %s OFFSET %s" # Default order by id ASC
        offset = (page - 1) * limit
        
        final_query = base_select + where_clause + query_pagination
        final_params = tuple(params + [limit, offset])

        with conn.cursor() as cursor:
            cursor.execute(final_query, final_params)
            users_page = cursor.fetchall()

        conn.close()

        for user in users_page:
            if user.get('avatar'):
                user['has_avatar'] = True
                user.pop('avatar')
            else:
                user['has_avatar'] = False
                if 'avatar' in user:
                    user.pop('avatar')
        
        return jsonify({'code': 20000, 'data': {'users': users_page, 'total': total_count}})
    except Exception as e:
        current_app.logger.error(f"Error fetching web users: {e}")
        return jsonify({'code': 50000, 'message': f'获取Web端用户列表失败: {str(e)}'}), 500

@user_bp.route('/web', methods=['POST'])
@role_required(['super_admin', 'admin'])
def create_web_user(current_user_from_decorator, **kwargs):
    """创建Web端用户 (已更新, 使用 id)"""
    current_operator = current_user_from_decorator
    data = request.get_json()

    required_fields = ['username', 'password'] 
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'code': 40000, 'message': f'{field}不能为空'}), 400

    try:
        conn = get_cloud_db_connection()
        existing_user = WebUser.get_user_by_username(conn, data['username'])
        if existing_user:
            conn.close()
            return jsonify({'code': 40000, 'message': '用户名已存在'}), 400

        user_data = {
            'username': data['username'],
            'password': data['password'],
            'email': data.get('email'),
            'status': data.get('status', '正常')
        }
        user_data_to_create = {k: v for k, v in user_data.items() if v is not None or k in required_fields}
        
        if user_data_to_create['status'] not in ['正常', '禁用']:
            conn.close()
            return jsonify({'code': 40000, 'message': '无效的用户状态值'}), 400

        new_user_actual_id = WebUser.create_user(conn, user_data_to_create)
        # 获取新创建用户的信息，模型返回的是id
        new_user_info = WebUser.get_user(conn, new_user_actual_id) if new_user_actual_id else {"username": data['username'], "id": new_user_actual_id} 
        conn.close()

        log = OperationLog(
            admin_id=current_operator.id,
            admin_username=current_operator.username,
            operation_type='用户管理',
            # 使用 new_user_actual_id 记录日志
            operation_content=f'创建Web端用户 {new_user_info.get("username", "N/A")} (ID: {new_user_actual_id})',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        # 返回给前端的 user 对象也应该包含 id 而不是 userid
        return jsonify({'code': 20000, 'message': 'Web端用户创建成功', 'data': {'user': new_user_info}}), 201
    except Exception as e:
        current_app.logger.error(f"Error creating web user: {e}")
        if 'conn' in locals() and conn and conn.open: conn.close()
        return jsonify({'code': 50000, 'message': f'创建Web端用户失败: {str(e)}'}), 500


@user_bp.route('/web/<int:user_id>', methods=['PUT'])
@role_required(['super_admin', 'admin'])
def update_web_user(user_id, current_user_from_decorator, **kwargs):
    """更新Web用户信息 (已更新)"""
    current_operator = current_user_from_decorator
    data = request.get_json()

    if not data:
        return jsonify({'code': 40000, 'message': '未提供更新数据'}), 400

    try:
        conn = get_cloud_db_connection()
        user_to_update = WebUser.get_user(conn, user_id) # Model uses userid
        if not user_to_update:
            conn.close()
            return jsonify({'code': 40400, 'message': 'Web端用户不存在'}), 404
        
        update_payload = {}
         # Fields are now username, email, status, password
        allowed_fields_to_update = ['username', 'email', 'status', 'password']
        for field in allowed_fields_to_update:
            if field in data: # Check if field is in request data
                update_payload[field] = data[field]
        
        if 'status' in update_payload and update_payload['status'] not in ['正常', '禁用']:
            conn.close()
            return jsonify({'code': 40000, 'message': '无效的用户状态值'}), 400

        if 'username' in update_payload and update_payload['username'] != user_to_update.get('username'):
            existing_user = WebUser.get_user_by_username(conn, update_payload['username'])
            if existing_user and existing_user.get('userid') != user_id:
                conn.close()
                return jsonify({'code': 40000, 'message': '该用户名已被其他用户使用'}), 400

        if not update_payload:
            conn.close()
            return jsonify({'code': 40000, 'message': '没有有效字段可供更新'}), 400
            
        WebUser.update_user(conn, user_id, update_payload) # Model uses userid
        updated_user_info = WebUser.get_user(conn, user_id)
        conn.close()

        log = OperationLog(
            admin_id=current_operator.id,
            admin_username=current_operator.username,
            operation_type='用户管理',
            operation_content=f'更新Web端用户 {updated_user_info.get("username", "N/A")} (ID: {user_id})。详情: {json.dumps(update_payload)}',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()

        return jsonify({'code': 20000, 'message': 'Web端用户信息更新成功', 'data': {'user': updated_user_info}})
    except Exception as e:
        current_app.logger.error(f"Error updating web user {user_id}: {e}")
        if 'conn' in locals() and conn and conn.open: conn.close()
        return jsonify({'code': 50000, 'message': f'更新Web端用户信息失败: {str(e)}'}), 500


@user_bp.route('/web/<int:user_id>', methods=['DELETE'])
@role_required(['super_admin', 'admin'])
def delete_web_user(user_id, current_user_from_decorator, **kwargs):
    """删除Web用户 (已更新)"""
    current_operator = current_user_from_decorator
    try:
        conn = get_cloud_db_connection()
        user_to_delete = WebUser.get_user(conn, user_id) # Model uses userid
        if not user_to_delete:
            conn.close()
            return jsonify({'code': 40400, 'message': 'Web端用户不存在'}), 404

        username_deleted = user_to_delete.get('username', 'N/A') # Get username
        WebUser.delete_user(conn, user_id) # Model uses userid
        conn.close()

        log = OperationLog(
            admin_id=current_operator.id,
            admin_username=current_operator.username,
            operation_type='用户管理',
            operation_content=f'删除Web端用户 {username_deleted} (ID: {user_id})',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()

        return jsonify({'code': 20000, 'message': 'Web端用户删除成功'})
    except Exception as e:
        current_app.logger.error(f"Error deleting web user {user_id}: {e}")
        if 'conn' in locals() and conn and conn.open: conn.close()
        return jsonify({'code': 50000, 'message': f'删除Web端用户失败: {str(e)}'}), 500 