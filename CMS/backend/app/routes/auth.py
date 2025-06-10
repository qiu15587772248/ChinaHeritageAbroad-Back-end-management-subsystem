from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models.user import AdminUser
from app.models.log import OperationLog
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """管理员登录接口"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # <<< 新增调试信息
    print(f"[AUTH DEBUG] Received login request for username: '{username}'")
    # 为了安全，不在生产环境中打印密码明文，但在调试阶段可以临时使用
    # print(f"[AUTH DEBUG] Received password: '{password}'") 
    # >>> 结束新增调试信息
    
    if not username or not password:
        # <<< 新增调试信息
        print(f"[AUTH DEBUG] Username or password not provided.")
        # >>> 结束新增调试信息
        return jsonify({'message': '用户名和密码不能为空'}), 400
        
    user = AdminUser.query.filter_by(username=username).first()
    
    # <<< 新增调试信息
    if not user:
        print(f"[AUTH DEBUG] User '{username}' not found in database.")
    else:
        print(f"[AUTH DEBUG] User '{username}' found. DB password: '{user.password}', Provided password: '{password}'")
        verification_result = user.verify_password(password)
        print(f"[AUTH DEBUG] Password verification result for '{username}': {verification_result}")
    # >>> 结束新增调试信息
    
    if user and user.verify_password(password):
        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # 记录操作日志
        log = OperationLog(
            admin_id=user.id,
            admin_username=user.username,
            operation_type='login',
            operation_content=f'用户 {username} 登录系统',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        # 创建访问令牌, 暂时恢复 identity 为不含 role
        access_token = create_access_token(
            identity={'id': user.id, 'username': user.username}, # 恢复: 移除 role
            expires_delta=timedelta(hours=8)
        )
        # <<< 新增调试信息
        print(f"[AUTH DEBUG] Login successful for '{username}'. Token created.")
        # >>> 结束新增调试信息
        
        return jsonify({
            'message': '登录成功',
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })
    else:
        # <<< 新增调试信息
        print(f"[AUTH DEBUG] Login failed for '{username}'. Invalid credentials.")
        # >>> 结束新增调试信息
        return jsonify({'message': '用户名或密码错误'}), 401


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """修改密码接口"""
    identity = get_jwt_identity()
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        return jsonify({'message': '原密码和新密码不能为空'}), 400
        
    user = AdminUser.query.get(identity['id'])
    
    if not user:
        return jsonify({'message': '用户不存在'}), 404
        
    if not user.verify_password(old_password):
        return jsonify({'message': '原密码错误'}), 401
        
    user.password = new_password
    db.session.commit()
    
    # 记录操作日志
    log = OperationLog(
        admin_id=user.id,
        admin_username=user.username,
        operation_type='password_change',
        operation_content=f'用户 {user.username} 修改了密码',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'message': '密码修改成功'})


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """获取当前用户资料"""
    identity = get_jwt_identity() # identity 现在会包含 role
    # 确保 identity 格式正确
    if not isinstance(identity, dict) or 'id' not in identity:
        return jsonify(message="无效的令牌格式或缺少用户ID"), 401

    user = AdminUser.query.get(identity['id'])
    
    if not user:
        return jsonify({'message': '用户不存在'}), 404
        
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': getattr(user, 'role', 'admin'), # 从数据库对象获取role，更可靠
        'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else None,
        'last_login': user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else None
    }) 