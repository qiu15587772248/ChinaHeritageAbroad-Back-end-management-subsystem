import pymysql
from flask import current_app

def get_db_connection():
    """获取数据库连接"""
    conn = pymysql.connect(
        host=current_app.config['DB_HOST'],
        user=current_app.config['DB_USER'],
        password=current_app.config['DB_PASSWORD'],
        database=current_app.config['DB_NAME'],
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn

def execute_query(sql, params=None, fetch=True):
    """执行SQL查询"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            if fetch:
                return cursor.fetchall()
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def execute_update(sql, params=None):
    """执行SQL更新"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            result = cursor.execute(sql, params or ())
        conn.commit()
        return result
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def batch_execute(sql, params_list):
    """批量执行SQL"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            result = cursor.executemany(sql, params_list)
        conn.commit()
        return result
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close() 