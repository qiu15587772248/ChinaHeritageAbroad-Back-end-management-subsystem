from flask import Blueprint, request, jsonify, current_app
from app import db # For OperationLog
from app.models.log import OperationLog
from app.models.user import AdminUser, CloudUser # For updating mobile_user status
from .user import get_cloud_db_connection, role_required # For DB connection and auth
from datetime import datetime

review_bp = Blueprint('review', __name__)

# Helper to add operation log
def add_review_log(admin_username, content):
    # In a real app, get current admin user properly
    # For now, assuming admin_username is passed or known
    # A more robust way would be to get admin_id from JWT like in other routes
    admin_user = AdminUser.query.filter_by(username=admin_username).first()
    admin_id_to_log = admin_user.id if admin_user else 0 # Default to 0 if not found, or handle error

    log = OperationLog(
        admin_id=admin_id_to_log, # This needs to be the ID of the admin performing the action
        admin_username=admin_username, # Username of the admin
        operation_type='信息审核', # Unified type for review operations
        operation_content=content,
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()

@review_bp.route('/comments', methods=['GET'])
@role_required(['admin', 'super_admin'])
def get_pending_comments(current_user_from_decorator, **kwargs):
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    passed_status = request.args.get('passed', None) # '0' for not passed, '1' for passed, None for all
    search_keyword = request.args.get('keyword', '', type=str)
    user_identifier = request.args.get('user', '', type=str) # Can be userid or username

    conn = None
    try:
        conn = get_cloud_db_connection()
        with conn.cursor() as cursor:
            base_query = """
                SELECT c.id, c.user_id, c.artifact_id, c.comment, c.comment_time, c.passed,
                       mu.username as mobile_username, mu.status as mobile_user_status
                FROM comments c
                LEFT JOIN mobile_users mu ON c.user_id = mu.userid
            """
            count_query = """
                SELECT COUNT(c.id) as total
                FROM comments c
                LEFT JOIN mobile_users mu ON c.user_id = mu.userid
            """
            
            conditions = []
            params = []

            if passed_status is not None and passed_status in ['0', '1']:
                conditions.append("c.passed = %s")
                params.append(int(passed_status))
            
            if search_keyword:
                conditions.append("(c.comment LIKE %s OR mu.username LIKE %s)") # Search in comment or username
                params.extend([f"%{search_keyword}%", f"%{search_keyword}%"])
            
            if user_identifier:
                if user_identifier.isdigit():
                    conditions.append("c.user_id = %s")
                    params.append(int(user_identifier))
                else: # assume it is a username if not digit
                    conditions.append("mu.username = %s")
                    params.append(user_identifier)

            where_clause = ""
            if conditions:
                where_clause = " WHERE " + " AND ".join(conditions)
            
            # Get total count with filters
            cursor.execute(count_query + where_clause, tuple(params))
            total_count = cursor.fetchone()['total']

            # Get paginated data
            query_pagination = f" ORDER BY c.comment_time DESC LIMIT %s OFFSET %s"
            offset = (page - 1) * limit
            final_params = tuple(params + [limit, offset])
            
            cursor.execute(base_query + where_clause + query_pagination, final_params)
            comments_page = cursor.fetchall()

        return jsonify({
            'code': 20000,
            'data': {
                'comments': comments_page,
                'total': total_count,
                'page': page,
                'limit': limit
            }
        })

    except Exception as e:
        current_app.logger.error(f"Error fetching comments for review: {e}")
        return jsonify({'code': 50000, 'message': f'获取评论列表失败: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()

@review_bp.route('/comments/<int:comment_id>/status', methods=['PUT'])
@role_required(['admin', 'super_admin'])
def update_comment_status(comment_id, current_user_from_decorator, **kwargs):
    data = request.get_json()
    new_passed_status = data.get('passed')

    if new_passed_status is None or new_passed_status not in [0, 1]:
        return jsonify({'code': 40000, 'message': '无效的审核状态值，必须是0或1'}), 400

    conn = None
    try:
        conn = get_cloud_db_connection()
        with conn.cursor() as cursor:
            # Check if comment exists
            cursor.execute("SELECT id FROM comments WHERE id = %s", (comment_id,))
            comment = cursor.fetchone()
            if not comment:
                return jsonify({'code': 40400, 'message': '评论不存在'}), 404
            
            cursor.execute("UPDATE comments SET passed = %s WHERE id = %s", (new_passed_status, comment_id))
            conn.commit()
        
        status_text = "通过" if new_passed_status == 1 else "不通过"
        add_review_log(current_user_from_decorator.username, f'审核评论 (ID: {comment_id})，状态更新为: {status_text}')
        return jsonify({'code': 20000, 'message': '评论审核状态更新成功'})
    except Exception as e:
        if conn: conn.rollback()
        current_app.logger.error(f"Error updating comment status for ID {comment_id}: {e}")
        return jsonify({'code': 50000, 'message': f'更新评论审核状态失败: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()

@review_bp.route('/users/<int:user_id>/status', methods=['PUT'])
@role_required(['admin', 'super_admin'])
def update_mobile_user_status_by_review(user_id, current_user_from_decorator, **kwargs):
    data = request.get_json()
    new_status = data.get('status')

    if not new_status or new_status not in ['正常', '禁用']:
        return jsonify({'code': 40000, 'message': '无效的用户状态值，必须是 \'正常\' 或 \'禁用\''}), 400

    # Use CloudUser model methods if possible, or direct SQL
    conn = None
    try:
        # Check if user exists first (optional, update_user might handle it)
        conn = get_cloud_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT userid, username FROM mobile_users WHERE userid = %s", (user_id,))
            user = cursor.fetchone()
            if not user:
                return jsonify({'code': 40400, 'message': '移动端用户不存在'}), 404
            username_for_log = user['username']

            # Update using direct SQL as CloudUser.update_user might expect more fields or different structure
            cursor.execute("UPDATE mobile_users SET status = %s WHERE userid = %s", (new_status, user_id))
            conn.commit()

        add_review_log(current_user_from_decorator.username, f'更新移动端用户 (ID: {user_id}, 用户名: {username_for_log}) 状态为: {new_status}')
        return jsonify({'code': 20000, 'message': '移动端用户状态更新成功'})
    except Exception as e:
        if conn: conn.rollback()
        current_app.logger.error(f"Error updating mobile user status for ID {user_id}: {e}")
        return jsonify({'code': 50000, 'message': f'更新移动端用户状态失败: {str(e)}'}), 500
    finally:
        if conn:
            conn.close() 