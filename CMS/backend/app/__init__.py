from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from apscheduler.schedulers.background import BackgroundScheduler
from config import config
import os

from .utils.moderation import contains_sensitive_word, DEFAULT_SENSITIVE_WORDS
from .utils.db import get_db_connection 
from datetime import datetime 


# 初始化扩展
db = SQLAlchemy()
jwt = JWTManager()
scheduler = BackgroundScheduler()

def create_app(config_name='default'):
    app = Flask(__name__)

    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    CORS(app) # 保留
    
    # 确保备份目录存在
    if not os.path.exists(app.config['BACKUP_DIR']):
        os.makedirs(app.config['BACKUP_DIR'])
        
    # 确保日志目录存在
    if not os.path.exists(app.config['LOG_DIR']):
        os.makedirs(app.config['LOG_DIR'])
    
    # 注册蓝图
    from .routes.auth import auth_bp
    from .routes.user import user_bp
    from .routes.heritage import heritage_bp
    from .routes.backup import backup_bp
    from .routes.log import log_bp
    from .routes.dashboard import dashboard_bp
    from .routes.review import review_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(heritage_bp, url_prefix='/api/heritage')
    app.register_blueprint(backup_bp, url_prefix='/api/backup')
    app.register_blueprint(log_bp, url_prefix='/api/logs')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(review_bp, url_prefix='/api/reviews')
    
    # 定时任务函数 - 自动审核评论
    def auto_moderate_comments():

        with app.app_context(): 
            app.logger.info("Starting automatic comment moderation task...")
            conn = None
            try:
                conn = get_db_connection() 
                with conn.cursor() as cursor:
                    query = "SELECT id, comment FROM comments WHERE passed = 1"
                    cursor.execute(query)
                    comments_to_review = cursor.fetchall()
                    
                    processed_count = 0 
                    sensitive_updated_count = 0 

                    if not comments_to_review:
                        app.logger.info("No comments with passed=1 found for moderation at this time.")
                        return 

                    for comment_row in comments_to_review:
                        comment_id = comment_row['id']
                        comment_text = comment_row['comment']
                        processed_count += 1
                        
                        if contains_sensitive_word(comment_text, DEFAULT_SENSITIVE_WORDS):
                            update_query = "UPDATE comments SET passed = 0 WHERE id = %s"
                            cursor.execute(update_query, (comment_id,))
                            app.logger.info(f"Comment ID {comment_id} automatically marked as not passed (sensitive content found).")
                            sensitive_updated_count += 1

                    
                    if sensitive_updated_count > 0: 
                        conn.commit()
                        app.logger.info(f"Moderation task: {sensitive_updated_count} comment(s) updated to passed=0 due to sensitive content.")

                    app.logger.info(f"Automatic comment moderation task finished. Reviewed: {processed_count} comments. Updated due to sensitive content: {sensitive_updated_count}.")

            except Exception as e:
                if conn and conn.open: 
                    try:
                        conn.rollback()
                        app.logger.warning("Transaction rolled back due to error in moderation task.")
                    except Exception as rb_e:
                        app.logger.error(f"Error during rollback: {rb_e}")
                app.logger.error(f"Error during comment moderation task: {e}", exc_info=True)
            finally:
                if conn and conn.open: 
                    conn.close()

    # 启动定时任务
    from .utils.backup import schedule_backup 
    
    with app.app_context(): 

        if not scheduler.get_job('auto_moderate_comments_task'):
            scheduler.add_job(id='auto_moderate_comments_task', func=auto_moderate_comments, trigger='interval', minutes=1, misfire_grace_time=60)
            app.logger.info("Automatic comment moderation task has been scheduled.")
        else:
            app.logger.info("Automatic comment moderation task was already scheduled.")


        schedule_backup() 


        if not scheduler.running:
            try:
                scheduler.start()
                app.logger.info("APScheduler started.")
            except Exception as e: 
                app.logger.error(f"Failed to start APScheduler: {e}", exc_info=True)
        else:
            app.logger.info("APScheduler is already running.")

    return app 