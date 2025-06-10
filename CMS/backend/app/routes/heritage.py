from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import AdminUser
from app.models.heritage import MetClear
from app.models.log import OperationLog
import pymysql
import json
import functools

heritage_bp = Blueprint('heritage', __name__)

# 权限检查装饰器
def heritage_require_permission(permission):
    def decorator(fn):
        @jwt_required()
        @functools.wraps(fn)  # 这保留了原始函数的名称和元数据
        def wrapper(*args, **kwargs):
            identity = get_jwt_identity()
            user = AdminUser.query.get(identity['id'])
            
            if not user:
                return jsonify({'message': '用户不存在'}), 404
                
            if not user.has_permission(permission):
                return jsonify({'message': '权限不足'}), 403
                
            return fn(*args, **kwargs)
        return wrapper
    return decorator


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


@heritage_bp.route('/met-clear', methods=['GET'])
@jwt_required()
def get_met_clear_items():
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=10, type=int)
    title_filter = request.args.get('title', '')
    artist_filter = request.args.get('artist', '')
    classify_filter = request.args.get('classify', '')
    
    # 获取排序参数
    sort_by = request.args.get('sort_by', 'id')
    order = request.args.get('order', 'asc').lower() # 前端已设为asc，这里转小写确保一致

    # 参数校验
    allowed_sort_columns = ['id', 'title', 'artist', 'age', 'classify'] # 可根据实际情况调整允许排序的列
    if sort_by not in allowed_sort_columns:
        sort_by = 'id' # 如果传入无效列名，则默认按id排序
    if order not in ['asc', 'desc']:
        order = 'asc' # 如果传入无效排序方向，则默认升序
    
    try:
        conn = get_cloud_db_connection()
        with conn.cursor() as cursor:
            base_query = "FROM met_clear"
            count_query = f"SELECT COUNT(*) as total {base_query}"
            data_query = f"SELECT * {base_query}"
            
            conditions = []
            params = []

            # Build conditions based on individual filters
            if title_filter:
                conditions.append("title LIKE %s")
                params.append(f'%{title_filter}%')
            if artist_filter:
                conditions.append("artist LIKE %s")
                params.append(f'%{artist_filter}%')
            if classify_filter:
                # Assuming the database column name is 'classify' for the "分类" field
                conditions.append("classify LIKE %s") 
                params.append(f'%{classify_filter}%')
            
            if conditions:
                where_clause = " WHERE " + " AND ".join(conditions)
                count_query += where_clause
                data_query += where_clause

            cursor.execute(count_query, tuple(params))
            total_records_result = cursor.fetchone()
            total_records = total_records_result['total'] if total_records_result else 0
            
            # Add LIMIT and OFFSET for pagination AFTER filtering and counting
            # Need to re-add params for pagination if they were used in conditions for count
            pagination_params = list(params) 
            pagination_params.extend([limit, (page - 1) * limit])
            
            # 构建动态的 ORDER BY 子句
            # 注意: 直接将 sort_by 和 order 拼接到SQL字符串中，需要确保这两个变量是安全的
            # (已经通过上面的校验来限制允许的值)
            data_query += f" ORDER BY `{sort_by}` {order.upper()} LIMIT %s OFFSET %s"
            
            cursor.execute(data_query, tuple(pagination_params))
            items = cursor.fetchall()
        conn.close()
        return jsonify({
            'code': 20000, 
            'data': {
                'total': total_records,
                'items': items
            }
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching met_clear items: {e}")
        return jsonify({'code': 50000, 'message': f'获取数据失败: {str(e)}'}), 500


@heritage_bp.route('/met-clear/<int:item_id>', methods=['GET'])
@jwt_required()
def get_met_clear_item(item_id):
    try:
        conn = get_cloud_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM met_clear WHERE id = %s", (item_id,))
            item = cursor.fetchone()
        conn.close()
        if item:
            return jsonify({'code': 20000, 'data': item}), 200
        else:
            return jsonify({'code': 40400, 'message': '记录未找到'}), 404
    except Exception as e:
        current_app.logger.error(f"Error fetching met_clear item {item_id}: {e}")
        return jsonify({'code': 50000, 'message': '获取详情失败'}), 500


@heritage_bp.route('/met-clear', methods=['POST'])
@jwt_required()
def create_met_clear_item():
    data = request.get_json()
    if not data:
        return jsonify({'code': 40000, 'message': '请求数据不能为空'}), 400
    
    try:
        conn = get_cloud_db_connection()
        with conn.cursor() as cursor:
            fields = '`, `'.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            sql = f"INSERT INTO `met_clear` (`{fields}`) VALUES ({placeholders})"
            cursor.execute(sql, list(data.values()))
            new_id = cursor.lastrowid
        conn.commit()
        conn.close()
        identity = get_jwt_identity()
        admin = AdminUser.query.get(identity['id'])
        log = OperationLog(admin_id=admin.id, admin_username=admin.username, operation_type='create_heritage', operation_content=f'创建文物(met_clear): ID {new_id}', ip_address=request.remote_addr)
        db.session.add(log)
        db.session.commit()
        return jsonify({'code': 20000, 'data': {'id': new_id}, 'message': '创建成功'}), 201
    except Exception as e:
        current_app.logger.error(f"Error creating met_clear item: {e}")
        conn.rollback()
        return jsonify({'code': 50000, 'message': f'创建失败: {str(e)}'}), 500
    finally:
        if conn and conn.open: conn.close()


@heritage_bp.route('/met-clear/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_met_clear_item(item_id):
    data = request.get_json()
    if not data:
        return jsonify({'code': 40000, 'message': '请求数据不能为空'}), 400

    try:
        conn = get_cloud_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM met_clear WHERE id = %s", (item_id,))
            if not cursor.fetchone():
                conn.close()
                return jsonify({'code': 40400, 'message': '记录未找到'}), 404
            
            set_clause = ', '.join([f"`{key}` = %s" for key in data.keys()])
            values = list(data.values())
            values.append(item_id)
            sql = f"UPDATE `met_clear` SET {set_clause} WHERE `id` = %s"
            cursor.execute(sql, tuple(values))
        conn.commit()
        identity = get_jwt_identity()
        admin = AdminUser.query.get(identity['id'])
        log = OperationLog(admin_id=admin.id, admin_username=admin.username, operation_type='update_heritage', operation_content=f'更新文物(met_clear): ID {item_id}', ip_address=request.remote_addr)
        db.session.add(log)
        db.session.commit()
        return jsonify({'code': 20000, 'message': '更新成功'}), 200
    except Exception as e:
        current_app.logger.error(f"Error updating met_clear item {item_id}: {e}")
        conn.rollback()
        return jsonify({'code': 50000, 'message': f'更新失败: {str(e)}'}), 500
    finally:
        if conn and conn.open: conn.close()


@heritage_bp.route('/met-clear/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_met_clear_item(item_id):
    try:
        conn = get_cloud_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM met_clear WHERE id = %s", (item_id,))
            if not cursor.fetchone():
                conn.close()
                return jsonify({'code': 40400, 'message': '记录未找到'}), 404
            cursor.execute("DELETE FROM met_clear WHERE id = %s", (item_id,))
        conn.commit()
        identity = get_jwt_identity()
        admin = AdminUser.query.get(identity['id'])
        log = OperationLog(admin_id=admin.id, admin_username=admin.username, operation_type='delete_heritage', operation_content=f'删除文物(met_clear): ID {item_id}', ip_address=request.remote_addr)
        db.session.add(log)
        db.session.commit()
        return jsonify({'code': 20000, 'message': '删除成功'}), 200
    except Exception as e:
        current_app.logger.error(f"Error deleting met_clear item {item_id}: {e}")
        conn.rollback()
        return jsonify({'code': 50000, 'message': f'删除失败: {str(e)}'}), 500
    finally:
        if conn and conn.open: conn.close()


@heritage_bp.route('/met-clear/batch-delete', methods=['DELETE'])
@jwt_required() # 或者使用 @heritage_require_permission 如果有特定的批量删除权限
def batch_delete_met_clear_items():
    data = request.get_json()
    if not data or 'ids' not in data:
        return jsonify({'code': 40000, 'message': '请求数据无效，缺少ids字段'}), 400

    item_ids = data.get('ids')
    if not isinstance(item_ids, list) or not item_ids:
        return jsonify({'code': 40000, 'message': 'ids必须是一个非空列表'}), 400

    if not all(isinstance(item_id, int) for item_id in item_ids):
        return jsonify({'code': 40000, 'message': 'ids列表中的所有ID必须是整数'}), 400

    conn = None  # Ensure conn is defined for finally block
    try:
        conn = get_cloud_db_connection()
        with conn.cursor() as cursor:
            # 构建占位符字符串, e.g., (%s, %s, %s)
            placeholders = ', '.join(['%s'] * len(item_ids))
            # SQL语句，使用IN子句进行批量删除
            sql = f"DELETE FROM met_clear WHERE id IN ({placeholders})"
            
            # 执行删除操作
            rows_deleted = cursor.execute(sql, tuple(item_ids))
        
        conn.commit() # 提交事务

        identity = get_jwt_identity()
        admin = AdminUser.query.get(identity['id'])
        log_content = f'批量删除文物(met_clear): 共 {rows_deleted} 条, IDs: {json.dumps(item_ids)}'
        if len(log_content) > 255: # 假设 operation_content 长度限制为255
            log_content = f'批量删除文物(met_clear): 共 {rows_deleted} 条, IDs: {json.dumps(item_ids)[:200]}...'
        
        log = OperationLog(
            admin_id=admin.id, 
            admin_username=admin.username, 
            operation_type='batch_delete_heritage', # 新的操作类型
            operation_content=log_content, 
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit() # 提交日志事务

        return jsonify({'code': 20000, 'message': f'成功删除 {rows_deleted} 条记录'}), 200

    except Exception as e:
        if conn: conn.rollback() # 如果发生错误，回滚事务
        current_app.logger.error(f"Error batch deleting met_clear items: {e}")
        return jsonify({'code': 50000, 'message': f'批量删除失败: {str(e)}'}), 500
    finally:
        if conn and conn.open:
            conn.close() 