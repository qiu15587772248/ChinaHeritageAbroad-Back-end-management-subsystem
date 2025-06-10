import os
import datetime
import subprocess
import platform
from flask import current_app
from app import db, scheduler
from app.models.backup import BackupRecord

def create_backup(backup_type='auto', description='自动备份'):
    """创建数据库备份
    
    Args:
        backup_type: 备份类型，'auto' 或 'manual'
        description: 备份描述
        
    Returns:
        备份记录对象
    """
    # 生成备份文件名
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    backup_name = f"backup_{timestamp}.sql"
    backup_path = os.path.join(current_app.config['BACKUP_DIR'], backup_name)
    
    # 确保备份目录存在
    os.makedirs(current_app.config['BACKUP_DIR'], exist_ok=True)
    
    try:
        # 执行备份命令
        # 定义需要备份的表名列表
        tables_to_backup = [
            'admin_users', 
            'operation_logs', 
            'backup_records', 
            'mobile_users', 
            'web_users', 
            'met_clear',  # 文物列表依赖此表
            'comments'
            # artifacts 表已移除
            # loves 表根据用户需求不包含在此系统备份中

        ]
        tables_str = " ".join(tables_to_backup)

        if platform.system() == 'Windows':
            # Windows 环境
            cmd = f"mysqldump -h {current_app.config['DB_HOST']} -u {current_app.config['DB_USER']} -p{current_app.config['DB_PASSWORD']} {current_app.config['DB_NAME']} {tables_str} > {backup_path}"
        else:
            # Linux 环境
            cmd = f"mysqldump -h {current_app.config['DB_HOST']} -u {current_app.config['DB_USER']} -p{current_app.config['DB_PASSWORD']} {current_app.config['DB_NAME']} {tables_str} > {backup_path}"
        
        print(f"Executing backup command: {cmd}") # 打印到控制台
        current_app.logger.info(f"Executing backup command: {cmd}") # 打印到应用日志

        subprocess.run(cmd, shell=True, check=True)
        
        # 获取文件大小
        backup_size = os.path.getsize(backup_path)
        
        # 创建备份记录
        record = BackupRecord(
            backup_name=backup_name,
            backup_path=backup_path,
            backup_size=backup_size,
            backup_type=backup_type,
            status='success',
            description=description
        )
        db.session.add(record)
        db.session.commit()
        
        return record
        
    except Exception as e:
        # 备份失败，记录失败信息
        record = BackupRecord(
            backup_name=backup_name,
            backup_path=backup_path,
            backup_size=0,
            backup_type=backup_type,
            status='failed',
            description=f"{description}\n错误信息: {str(e)}"
        )
        db.session.add(record)
        db.session.commit()
        
        return record


def restore_backup(backup_id):
    """恢复数据库备份
    
    Args:
        backup_id: 备份记录ID
        
    Returns:
        恢复是否成功
    """
    record = BackupRecord.query.get(backup_id)
    
    if not record:
        raise ValueError('备份记录不存在')
        
    if not os.path.exists(record.backup_path):
        raise ValueError('备份文件不存在')
        
    try:
        # 执行恢复命令
        if platform.system() == 'Windows':
            # Windows 环境
            cmd = f"mysql -h {current_app.config['DB_HOST']} -u {current_app.config['DB_USER']} -p{current_app.config['DB_PASSWORD']} {current_app.config['DB_NAME']} < {record.backup_path}"
        else:
            # Linux 环境
            cmd = f"mysql -h {current_app.config['DB_HOST']} -u {current_app.config['DB_USER']} -p{current_app.config['DB_PASSWORD']} {current_app.config['DB_NAME']} < {record.backup_path}"
        
        subprocess.run(cmd, shell=True, check=True)
        return True
        
    except Exception as e:
        raise RuntimeError(f'恢复失败: {str(e)}')


def clean_old_backups(days=30):
    """清理旧备份文件
    
    Args:
        days: 保留的天数
        
    Returns:
        清理的备份数量
    """
    # 计算截止时间
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
    
    # 查询旧备份记录
    old_records = BackupRecord.query.filter(
        BackupRecord.backup_time < cutoff_date,
        BackupRecord.backup_type == 'auto'  # 只清理自动备份
    ).all()
    
    count = 0
    for record in old_records:
        try:
            # 删除备份文件
            if os.path.exists(record.backup_path):
                os.remove(record.backup_path)
                
            # 删除备份记录
            db.session.delete(record)
            count += 1
        except Exception:
            pass
            
    db.session.commit()
    return count


def schedule_backup():
    """设置定时备份任务，确保任务只添加一次。"""
    # 使用 app.logger 需要确保在 app context 中，或者 logger 已正确配置为可在后台线程使用
    # from flask import current_app # 如果要用 current_app.logger

    backup_job_id = 'scheduled_create_backup_task_v2' # 使用 v2 以区别旧的潜在任务
    clean_job_id = 'scheduled_clean_backups_task_v2'

    # 任务：每天凌晨3点执行备份
    if not scheduler.get_job(backup_job_id):
        scheduler.add_job(
            func=create_backup,
            trigger='cron',
            hour=3,
            minute=0,
            args=['auto', '定时备份'],
            id=backup_job_id,
            replace_existing=True, 
            misfire_grace_time=3600 
        )
    # 任务：每周日凌晨4点清理旧备份
    if not scheduler.get_job(clean_job_id):
        scheduler.add_job(
            func=clean_old_backups,
            trigger='cron',
            day_of_week='sun',
            hour=4,
            minute=0,
            id=clean_job_id,
            replace_existing=True,
            misfire_grace_time=3600
        )
