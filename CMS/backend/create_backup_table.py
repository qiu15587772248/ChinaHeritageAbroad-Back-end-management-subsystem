# CMS/backend/create_backup_table.py
import sys
import os
import pymysql # 直接使用 pymysql
import traceback

# --- Path setup ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GRANDPARENT_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))
sys.path.insert(0, GRANDPARENT_DIR)

# --- Imports for config ---
try:
    from CMS.backend.app import create_app # 只为获取配置
except ImportError as e:
    print(f"Error importing create_app: {e}")
    exit(1)

# --- Configuration ---
DB_CONFIG = {}
try:
    temp_app_for_config = create_app()
    DB_CONFIG['host'] = temp_app_for_config.config.get('DB_HOST')
    DB_CONFIG['port'] = temp_app_for_config.config.get('DB_PORT', 3306) # Default MySQL port
    DB_CONFIG['user'] = temp_app_for_config.config.get('DB_USER')
    DB_CONFIG['password'] = temp_app_for_config.config.get('DB_PASSWORD')
    DB_CONFIG['database'] = temp_app_for_config.config.get('DB_NAME')
    DB_CONFIG['charset'] = temp_app_for_config.config.get('DB_CHARSET', 'utf8mb4')
    del temp_app_for_config
except Exception as e:
    print(f"Error during create_app() or getting DB configuration: {e}")
    traceback.print_exc()
    exit(1)

# 检查是否所有必要的数据库配置都已获取
required_keys = ['host', 'user', 'password', 'database']
if not all(DB_CONFIG.get(key) for key in required_keys):
    print(f"Error: Missing one or more required database configurations: {required_keys}")
    print(f"Current DB_CONFIG: {DB_CONFIG}")
    exit(1)

# SQL statement to create the table if it doesn't exist
# (从之前的 BackupRecord 模型定义推断出的 SQL)
SQL_CREATE_BACKUP_RECORDS_TABLE = """
CREATE TABLE IF NOT EXISTS backup_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    backup_name VARCHAR(255) NOT NULL COMMENT '备份文件名',
    backup_path VARCHAR(512) NOT NULL COMMENT '备份文件服务器路径',
    backup_size VARCHAR(50) COMMENT '备份文件大小，例如 \\'10.5 MB\\'',
    backup_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '备份完成时间',
    backup_type VARCHAR(50) NOT NULL DEFAULT 'manual' COMMENT '备份类型 (manual, auto)',
    status VARCHAR(50) NOT NULL DEFAULT 'unknown' COMMENT '备份状态 (success, failed, in_progress)',
    description TEXT COMMENT '备份描述',
    restored_count INT DEFAULT 0 COMMENT '从此备份恢复的次数',
    last_restored_time DATETIME NULL COMMENT '最近一次从此备份恢复的时间'
) COMMENT '数据库备份记录表';
"""

def create_table_with_pymysql():
    conn = None
    try:
        print(f"Connecting to database '{DB_CONFIG['database']}' on host '{DB_CONFIG['host']}'...")
        conn = pymysql.connect(**DB_CONFIG)
        print("Database connection successful.")
        
        with conn.cursor() as cursor:
            print("Executing CREATE TABLE IF NOT EXISTS statement for 'backup_records'...")
            cursor.execute(SQL_CREATE_BACKUP_RECORDS_TABLE)
            print("Statement executed. 'backup_records' table should now exist if it didn't before.")
        
        conn.commit()
        print("Changes committed.")

    except pymysql.MySQLError as e:
        print(f"PyMySQL Error during table creation: {e}")
        traceback.print_exc()
        if conn:
            conn.rollback()
            print("Transaction rolled back.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        traceback.print_exc()
        if conn:
            conn.rollback()
            print("Transaction rolled back.")
    finally:
        if conn and conn.open:
            conn.close()
            print("Database connection closed.")

if __name__ == '__main__':
    print("Starting table creation script using direct pymysql...")
    
    # 我们不再需要检查模型文件是否存在，因为我们直接用SQL
    # model_file_path = os.path.join(SCRIPT_DIR, 'app', 'models', 'backup.py')
    # if not os.path.exists(model_file_path):
    #     print(f"Error: Model file '{model_file_path}' not found.")
    #     exit(1)
        
    create_table_with_pymysql()
    print("Table creation script finished.")
