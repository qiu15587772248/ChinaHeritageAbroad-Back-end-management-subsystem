from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.log import OperationLog
from datetime import datetime, timedelta

# Attempt to import the role_required decorator from the user routes
# This assumes user.py is in the same directory or a proper Python path is set up
# If this causes an import error, the structure or import method needs adjustment.
from .user import role_required # Assuming user.py is in the same routes directory

log_bp = Blueprint('log', __name__)

@log_bp.route('', methods=['GET'])
@role_required(['admin', 'super_admin']) # All admins can view logs
def get_logs(current_user_from_decorator, **kwargs):
    """获取操作日志列表"""
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 10))
    operation_type = request.args.get('operation_type')
    admin_id = request.args.get('admin_id')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    keyword = request.args.get('keyword', '')
    
    # 构建查询
    query = OperationLog.query
    
    if operation_type:
        query = query.filter(OperationLog.operation_type == operation_type)
        
    if admin_id:
        query = query.filter(OperationLog.admin_id == admin_id)
        
    if start_time:
        try:
            start_datetime = datetime.strptime(start_time, '%Y-%m-%d')
            query = query.filter(OperationLog.operation_time >= start_datetime)
        except ValueError:
            pass
            
    if end_time:
        try:
            end_datetime = datetime.strptime(end_time, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(OperationLog.operation_time < end_datetime)
        except ValueError:
            pass
            
    if keyword:
        query = query.filter(OperationLog.operation_content.like(f'%{keyword}%'))
    
    # 获取分页数据
    total = query.count()
    offset = (page - 1) * size
    logs = query.order_by(OperationLog.operation_time.desc()).offset(offset).limit(size).all()
    
    return jsonify({
        'logs': [log.to_dict() for log in logs],
        'total': total,
        'page': page,
        'size': size,
        'pages': (total + size - 1) // size
    })


@log_bp.route('/overview', methods=['GET'])
@role_required(['admin', 'super_admin'])
def get_log_overview(current_user_from_decorator, **kwargs):
    """获取日志概览信息"""
    # 获取当日日志数量
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_logs_count = OperationLog.query.filter(OperationLog.operation_time >= today).count()
    
    # 获取本周日志数量
    week_start = today - timedelta(days=today.weekday())
    week_logs_count = OperationLog.query.filter(OperationLog.operation_time >= week_start).count()
    
    # 获取本月日志数量
    month_start = today.replace(day=1)
    month_logs_count = OperationLog.query.filter(OperationLog.operation_time >= month_start).count()
    
    # 获取总日志数量
    total_logs_count = OperationLog.query.count()
    
    # 获取各类型日志数量
    type_stats = db.session.query(
        OperationLog.operation_type,
        db.func.count(OperationLog.id)
    ).group_by(OperationLog.operation_type).all()
    
    # 获取最近一周每天的日志数量
    daily_stats = []
    for i in range(7):
        day = today - timedelta(days=i)
        next_day = day + timedelta(days=1)
        count = OperationLog.query.filter(
            OperationLog.operation_time >= day,
            OperationLog.operation_time < next_day
        ).count()
        daily_stats.append({
            'date': day.strftime('%Y-%m-%d'),
            'count': count
        })
    
    return jsonify({
        'today_logs_count': today_logs_count,
        'week_logs_count': week_logs_count,
        'month_logs_count': month_logs_count,
        'total_logs_count': total_logs_count,
        'type_stats': [
            {'type': type_name, 'count': count}
            for type_name, count in type_stats
        ],
        'daily_stats': daily_stats
    })


@log_bp.route('/export', methods=['GET'])
@role_required(['admin', 'super_admin'])
def export_logs(current_user_from_decorator, **kwargs):
    """导出操作日志"""
    operation_type = request.args.get('operation_type')
    admin_id = request.args.get('admin_id')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    keyword = request.args.get('keyword', '')
    
    # 构建查询
    query = OperationLog.query
    
    if operation_type:
        query = query.filter(OperationLog.operation_type == operation_type)
        
    if admin_id:
        query = query.filter(OperationLog.admin_id == admin_id)
        
    if start_time:
        try:
            start_datetime = datetime.strptime(start_time, '%Y-%m-%d')
            query = query.filter(OperationLog.operation_time >= start_datetime)
        except ValueError:
            pass
            
    if end_time:
        try:
            end_datetime = datetime.strptime(end_time, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(OperationLog.operation_time < end_datetime)
        except ValueError:
            pass
            
    if keyword:
        query = query.filter(OperationLog.operation_content.like(f'%{keyword}%'))
    
    # 获取所有符合条件的日志
    logs = query.order_by(OperationLog.operation_time.desc()).all()
    
    # 将日志转换为CSV格式
    # 使用 StringIO 来构建 CSV，更高效且避免大量字符串拼接
    import io
    si = io.StringIO()
    # 写入UTF-8 BOM头，确保Excel等软件能正确识别中文
    si.write('\ufeff') 
    
    # 写入CSV表头
    header = "ID,用户ID,用户名,操作类型,操作内容,操作时间,IP地址\n"
    si.write(header)
    
    # 写入数据行
    for log in logs:
        # 对于可能包含逗号或引号的内容，最好用双引号包裹，并对内部的双引号进行转义
        # 但为了简化，这里先保持原样，如果内容本身简单则问题不大
        operation_content_escaped = log.operation_content.replace('"', '""') # 简单处理引号
        si.write(f"{log.id},{log.admin_id or ''},{log.admin_username or ''},{log.operation_type or ''},\"{operation_content_escaped}\",{log.operation_time.strftime('%Y-%m-%d %H:%M:%S') if log.operation_time else ''},{log.ip_address or ''}\n")
    
    csv_data = si.getvalue()
    si.close()
    
    # 将Unicode字符串编码为UTF-8字节串
    byte_csv_data = csv_data.encode('utf-8')
    
    # 返回CSV文件
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f"logs_export_{timestamp}.csv"
    
    return Response(
        byte_csv_data,  # 使用编码后的字节串
        mimetype='text/csv; charset=utf-8',
        headers={'Content-Disposition': f'attachment;filename={filename}'}
    ) 