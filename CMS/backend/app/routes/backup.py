from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.backup import BackupRecord
from app.models.log import OperationLog
import os
import datetime
import subprocess
import platform

from .user import role_required

backup_bp = Blueprint('backup', __name__)

@backup_bp.route('', methods=['GET'])
@role_required(['admin', 'super_admin'])
def get_backup_records(current_user_from_decorator, **kwargs):
    """获取备份记录列表"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int) # 通常前端分页组件会发送 limit
        offset = (page - 1) * limit

        # 查询数据库
        records_query = BackupRecord.query.order_by(BackupRecord.backup_time.desc())
        total = records_query.count() # 获取总数
        records = records_query.offset(offset).limit(limit).all()

        # 将结果转换为字典列表
        results = [record.to_dict() for record in records]

        return jsonify({
            'code': 20000, # Vue Element Admin 通常期望的成功码
            'data': {
                'total': total,
                'items': results
            },
            'message': '获取备份列表成功'
        })
    except Exception as e:
        current_app.logger.error(f"Error fetching backup records: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'code': 50000, 'message': f'获取备份列表失败: {str(e)}'}), 500


@backup_bp.route('', methods=['POST'])
@role_required(['admin', 'super_admin'])
def create_backup(current_user_from_decorator, **kwargs):
    """创建数据库备份"""
    admin_user = current_user_from_decorator
    data = request.get_json()
    description = data.get('description', '')
    
    # 生成备份文件名
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    backup_name = f"backup_{timestamp}.sql"
    backup_path = os.path.join(current_app.config['BACKUP_DIR'], backup_name)
    
    # 确保备份目录存在
    os.makedirs(current_app.config['BACKUP_DIR'], exist_ok=True)
    
    try:
        # 执行备份命令
        if platform.system() == 'Windows':
            # Windows 环境
            cmd = f"mysqldump -h {current_app.config['DB_HOST']} -u {current_app.config['DB_USER']} -p{current_app.config['DB_PASSWORD']} {current_app.config['DB_NAME']} > {backup_path}"
        else:
            # Linux 环境
            cmd = f"mysqldump -h {current_app.config['DB_HOST']} -u {current_app.config['DB_USER']} -p{current_app.config['DB_PASSWORD']} {current_app.config['DB_NAME']} > {backup_path}"
        
        subprocess.run(cmd, shell=True, check=True)
        
        # 获取文件大小
        backup_size = os.path.getsize(backup_path)
        
        # 创建备份记录
        record = BackupRecord(
            backup_name=backup_name,
            backup_path=backup_path,
            backup_size=backup_size,
            backup_type='manual',
            status='success',
            description=description
        )
        db.session.add(record)
        db.session.commit()
        
        # 记录操作日志
        log = OperationLog(
            admin_id=admin_user.id,
            admin_username=admin_user.username,
            operation_type='backup',
            operation_content=f'创建数据库备份 (ID: {record.id}, 名称: {backup_name})',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'message': '备份成功',
            'record': record.to_dict()
        })
        
    except Exception as e:
        # 备份失败，记录失败信息
        record = BackupRecord(
            backup_name=backup_name,
            backup_path=backup_path,
            backup_size=0,
            backup_type='manual',
            status='failed',
            description=f"{description}\n错误信息: {str(e)}"
        )
        db.session.add(record)
        db.session.commit()
        
        return jsonify({'message': f'备份失败: {str(e)}'}), 500


@backup_bp.route('/<int:record_id>', methods=['GET'])
@role_required(['admin', 'super_admin'])
def download_backup(record_id, current_user_from_decorator, **kwargs):
    """下载备份文件"""
    record = BackupRecord.query.get(record_id)
    
    if not record:
        return jsonify({'message': '备份记录不存在'}), 404
        
    if not os.path.exists(record.backup_path):
        return jsonify({'message': '备份文件不存在'}), 404
        
    return send_file(record.backup_path, as_attachment=True)


@backup_bp.route('/<int:record_id>/restore', methods=['POST'])
@role_required(['admin', 'super_admin'])
def restore_backup(record_id, current_user_from_decorator, **kwargs):
    """恢复数据库备份"""
    admin_user = current_user_from_decorator
    record = BackupRecord.query.get(record_id)
    
    if not record:
        return jsonify({'message': '备份记录不存在'}), 404
        
    if not os.path.exists(record.backup_path):
        return jsonify({'message': '备份文件不存在'}), 404
        
    try:
        # 执行恢复命令
        if platform.system() == 'Windows':
            # Windows 环境
            cmd = f"mysql -h {current_app.config['DB_HOST']} -u {current_app.config['DB_USER']} -p{current_app.config['DB_PASSWORD']} {current_app.config['DB_NAME']} < {record.backup_path}"
        else:
            # Linux 环境
            cmd = f"mysql -h {current_app.config['DB_HOST']} -u {current_app.config['DB_USER']} -p{current_app.config['DB_PASSWORD']} {current_app.config['DB_NAME']} < {record.backup_path}"
        
        subprocess.run(cmd, shell=True, check=True)
        
        # 记录操作日志
        log = OperationLog(
            admin_id=admin_user.id,
            admin_username=admin_user.username,
            operation_type='restore',
            operation_content=f'恢复数据库备份 (ID: {record.id}, 名称: {record.backup_name})',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({'message': '恢复成功'})
        
    except Exception as e:
        return jsonify({'message': f'恢复失败: {str(e)}'}), 500


@backup_bp.route('/<int:record_id>', methods=['DELETE'])
@role_required(['admin', 'super_admin'])
def delete_backup(record_id, current_user_from_decorator, **kwargs):
    """删除备份记录"""
    admin_user = current_user_from_decorator
    record = BackupRecord.query.get(record_id)
    
    if not record:
        return jsonify({'message': '备份记录不存在'}), 404
        
    try:
        # 删除备份文件
        if os.path.exists(record.backup_path):
            os.remove(record.backup_path)
            
        # 记录操作日志
        log = OperationLog(
            admin_id=admin_user.id,
            admin_username=admin_user.username,
            operation_type='backup',
            operation_content=f'删除数据库备份 (ID: {record.id}, 名称: {record.backup_name})',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        
        # 删除备份记录
        db.session.delete(record)
        db.session.commit()
        
        return jsonify({'message': '删除成功'})
        
    except Exception as e:
        return jsonify({'message': f'删除失败: {str(e)}'}), 500 