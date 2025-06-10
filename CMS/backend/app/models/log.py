from app import db
from datetime import datetime

class OperationLog(db.Model):
    """操作日志模型"""
    __tablename__ = 'operation_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, nullable=False)
    admin_username = db.Column(db.String(50), nullable=False)
    operation_type = db.Column(db.String(50), nullable=False)  # 'user_manage', 'data_manage', 'backup', 'restore'
    operation_content = db.Column(db.Text)
    operation_time = db.Column(db.DateTime, default=datetime.now)
    ip_address = db.Column(db.String(50))
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'admin_id': self.admin_id,
            'admin_username': self.admin_username,
            'operation_type': self.operation_type,
            'operation_content': self.operation_content,
            'operation_time': self.operation_time.strftime('%Y-%m-%d %H:%M:%S'),
            'ip_address': self.ip_address
        } 