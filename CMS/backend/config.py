import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cms-secret-key'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    
    # 数据库连接配置 - 阿里云MySQL
    DB_HOST = os.environ.get('DB_HOST') or '39.105.26.212'
    DB_PORT = int(os.environ.get('DB_PORT') or 3306)
    DB_USER = os.environ.get('DB_USER') or 'museumdb'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or '123456'
    DB_NAME = os.environ.get('DB_NAME') or 'museumdb'
    
    # 默认使用阿里云MySQL数据库
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 备份配置
    BACKUP_DIR = os.environ.get('BACKUP_DIR') or 'backups'
    
    # 日志配置
    LOG_DIR = os.environ.get('LOG_DIR') or 'logs'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    # 测试时可以使用本地SQLite数据库
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 