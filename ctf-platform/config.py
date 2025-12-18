import os
from datetime import timedelta

class Config:
    """基础配置类"""
    
    # 应用密钥
    SECRET_KEY = os.environ.get('SECRET_KEY', 'L1BU0vHwj0NwS75duJ5EB1eiEGMw1GDj2FOOeI2hn46rfDAbvJB08qOBi0KgfqLg')
    
    # MySQL数据库配置
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT') or 3306)
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'ctf_user'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or '031006'
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE') or 'ctf_platform'
    
    # SQLAlchemy配置
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True
    }
    
    # JWT配置
    JWT_SECRET_KEY = SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'storage')
    CHALLENGE_ATTACHMENTS_FOLDER = os.path.join(UPLOAD_FOLDER, 'challenges')
    TEMP_FOLDER = os.path.join(UPLOAD_FOLDER, 'temp')
    
    # 平台配置
    PLATFORM_NAME = os.environ.get('PLATFORM_NAME') or 'CTF Platform'
    PLATFORM_DESCRIPTION = os.environ.get('PLATFORM_DESCRIPTION') or 'A Capture The Flag Platform'
    
    # 注册配置
    REGISTRATION_OPEN = os.environ.get('REGISTRATION_OPEN', 'true').lower() == 'true'
    REQUIRE_EMAIL_VERIFICATION = os.environ.get('REQUIRE_EMAIL_VERIFICATION', 'false').lower() == 'true'
    
    # 邮件配置（用于邮件验证和通知）
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@ctfplatform.com'
    
    # Redis配置（用于缓存和会话管理）
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.path.join(UPLOAD_FOLDER, 'logs', 'ctf_platform.log')
    
    # 安全配置
    RATE_LIMITING_ENABLED = os.environ.get('RATE_LIMITING_ENABLED', 'true').lower() == 'true'
    MAX_SUBMISSIONS_PER_MINUTE = int(os.environ.get('MAX_SUBMISSIONS_PER_MINUTE') or 30)
    
    # Flag配置
    FLAG_PREFIX = os.environ.get('FLAG_PREFIX') or 'CTF'
    FLAG_FORMAT = os.environ.get('FLAG_FORMAT') or 'static'  # static or dynamic
    FLAG_CASE_SENSITIVE = os.environ.get('FLAG_CASE_SENSITIVE', 'false').lower() == 'true'
    
    # 积分配置
    SCORING_SYSTEM = os.environ.get('SCORING_SYSTEM') or 'dynamic'  # static or dynamic
    BASE_POINTS = int(os.environ.get('BASE_POINTS') or 1000)
    BLOOD_BONUS_ENABLED = os.environ.get('BLOOD_BONUS_ENABLED', 'true').lower() == 'true'
    
    # 比赛配置
    DEFAULT_CONTEST_DURATION = int(os.environ.get('DEFAULT_CONTEST_DURATION') or 24)  # hours
    
    # 管理员配置
    ADMIN_USERNAMES = os.environ.get('ADMIN_USERNAMES', '').split(',')

class DevelopmentConfig(Config):
    """开发环境配置"""
    
    DEBUG = True
    TESTING = False
    
    # 开发环境使用更简单的数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        f'mysql+pymysql://{Config.MYSQL_USER}:{Config.MYSQL_PASSWORD}@{Config.MYSQL_HOST}:{Config.MYSQL_PORT}/{Config.MYSQL_DATABASE}'
    
    # 开发环境日志级别
    LOG_LEVEL = 'DEBUG'
    
    # 开发环境禁用部分安全限制
    RATE_LIMITING_ENABLED = False

class TestingConfig(Config):
    """测试环境配置"""
    
    DEBUG = False
    TESTING = True
    
    # 测试环境使用测试数据库
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        f'mysql+pymysql://{Config.MYSQL_USER}:{Config.MYSQL_PASSWORD}@{Config.MYSQL_HOST}:{Config.MYSQL_PORT}/{Config.MYSQL_DATABASE}_test'
    
    # 测试环境配置
    WTF_CSRF_ENABLED = False
    RATE_LIMITING_ENABLED = False

class ProductionConfig(Config):
    """生产环境配置"""
    
    DEBUG = False
    TESTING = False
    
    # 生产环境SECRET_KEY - 使用默认值而不是抛出异常
    SECRET_KEY = os.environ.get('SECRET_KEY', Config.SECRET_KEY)
    
    # 生产环境数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'mysql+pymysql://{Config.MYSQL_USER}:{Config.MYSQL_PASSWORD}@{Config.MYSQL_HOST}:{Config.MYSQL_PORT}/{Config.MYSQL_DATABASE}'
    
    # 生产环境安全配置
    RATE_LIMITING_ENABLED = True
    MAX_SUBMISSIONS_PER_MINUTE = 10  # 生产环境限制更严格

# 配置映射
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """获取当前环境配置"""
    env = os.environ.get('FLASK_ENV') or 'development'
    return config.get(env, config['default'])