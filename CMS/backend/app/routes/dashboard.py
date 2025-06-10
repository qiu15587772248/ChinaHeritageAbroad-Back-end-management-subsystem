from flask import Blueprint, jsonify, current_app
from app import db # For SQLAlchemy models like AdminUser, BackupRecord
from app.models.log import OperationLog
from app.models.user import AdminUser
# MetClear is not an SQLAlchemy model in the same way, it uses direct DB connections
# from app.models.heritage import MetClear # Remove this if MetClear is not a standard SQLAlchemy model here
from .user import get_cloud_db_connection # To connect to cloud DB for mobile_users, web_users, and met_clear
from datetime import datetime, date

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/stats', methods=['GET'])
def get_dashboard_stats():
    try:
        heritage_count = 0
        conn = None # Initialize conn outside try block for broader scope
        try:
            conn = get_cloud_db_connection()
            with conn.cursor() as cursor:
                # 1. 文物总数 (met_clear table)
                cursor.execute("SELECT COUNT(*) as count FROM met_clear")
                result = cursor.fetchone()
                if result:
                    heritage_count = result['count']
                
                # 2. 用户总数 (part 1: cloud users)
                mobile_user_count = 0
                cursor.execute("SELECT COUNT(*) as count FROM mobile_users")
                result = cursor.fetchone()
                if result:
                    mobile_user_count = result['count']
                
                web_user_count = 0
                cursor.execute("SELECT COUNT(*) as count FROM web_users")
                result = cursor.fetchone()
                if result:
                    web_user_count = result['count']
        except Exception as e:
            current_app.logger.error(f"Error fetching cloud data (heritage/users): {e}")
            # Depending on desired behavior, you might want to re-raise or return error here
        finally:
            if conn:
                conn.close()

        # 2. 用户总数 (part 2: admin users and total)
        admin_user_count = AdminUser.query.count() # This uses SQLAlchemy
        total_user_count = admin_user_count + mobile_user_count + web_user_count

        # 3. 备份数量 (backup_records table)
        from app.models.backup import BackupRecord # SQLAlchemy model
        backup_count = BackupRecord.query.count()

        # 4. 今日访问量 (管理员今日登录次数)
        today_start = datetime.combine(date.today(), datetime.min.time())
        today_logins = OperationLog.query.filter(
            OperationLog.operation_type == 'login',
            OperationLog.operation_time >= today_start
        ).count() # SQLAlchemy model

        # 5. 最近操作记录
        recent_logs = OperationLog.query.order_by(OperationLog.operation_time.desc()).limit(5).all()
        recent_logs_data = [log.to_dict() for log in recent_logs]

        return jsonify({
            'code': 20000,
            'data': {
                'heritage_count': heritage_count,
                'total_user_count': total_user_count,
                'admin_user_count': admin_user_count,
                'mobile_user_count': mobile_user_count,
                'web_user_count': web_user_count,
                'backup_count': backup_count,
                'today_visits': today_logins,
                'recent_logs': recent_logs_data
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching dashboard stats: {e}")
        return jsonify({'code': 50000, 'message': f'获取仪表盘数据失败: {str(e)}'}), 500 