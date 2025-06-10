from app import db
from datetime import datetime

class BackupRecord(db.Model):
    """数据库备份记录模型"""
    __tablename__ = 'backup_records'
    
    id = db.Column(db.Integer, primary_key=True)
    backup_name = db.Column(db.String(100), nullable=False)
    backup_path = db.Column(db.String(255), nullable=False)
    backup_size = db.Column(db.BigInteger)
    backup_time = db.Column(db.DateTime, default=datetime.now)
    backup_type = db.Column(db.String(20), nullable=False)  # 'manual', 'auto'
    status = db.Column(db.String(20), nullable=False)  # 'success', 'failed'
    description = db.Column(db.Text)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'backup_name': self.backup_name,
            'backup_size': self.backup_size,
            'backup_time': self.backup_time.strftime('%Y-%m-%d %H:%M:%S'),
            'backup_type': self.backup_type,
            'status': self.status,
            'description': self.description
        } 