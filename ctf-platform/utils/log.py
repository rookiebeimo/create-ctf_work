import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from datetime import datetime
from flask import request, current_app

def setup_logging(app):
    """设置日志配置"""
    
    # 创建日志目录
    log_dir = os.path.join(app.root_path, '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # 日志文件路径
    log_file = os.path.join(log_dir, 'ctf_platform.log')
    
    # 设置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s [in %(pathname)s:%(lineno)d]'
    )
    
    # 文件处理器（按大小轮转）
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=1024 * 1024 * 10,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)
    
    # 设置应用日志
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    
    # 移除默认的处理器
    app.logger.handlers = []
    app.logger.propagate = False
    
    # 添加自定义处理器
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)

def log_security_event(event_type, user_id, description, ip_address=None, severity='INFO'):
    """
    记录安全事件
    
    Args:
        event_type: 事件类型
        user_id: 用户ID
        description: 事件描述
        ip_address: IP地址
        severity: 严重程度
    """
    if not ip_address:
        ip_address = request.remote_addr if request else 'Unknown'
    
    logger = current_app.logger
    
    log_message = f"SECURITY - {event_type} - User:{user_id} - IP:{ip_address} - {description}"
    
    if severity.upper() == 'CRITICAL':
        logger.critical(log_message)
    elif severity.upper() == 'ERROR':
        logger.error(log_message)
    elif severity.upper() == 'WARNING':
        logger.warning(log_message)
    else:
        logger.info(log_message)

def log_submission(user_id, challenge_id, is_correct, submitted_flag=None):
    """
    记录提交日志
    
    Args:
        user_id: 用户ID
        challenge_id: 题目ID
        is_correct: 是否正确
        submitted_flag: 提交的Flag
    """
    logger = current_app.logger
    
    status = "CORRECT" if is_correct else "WRONG"
    
    # 保护敏感信息，不记录完整的Flag
    if submitted_flag:
        masked_flag = submitted_flag[:8] + "..." if len(submitted_flag) > 8 else submitted_flag
    else:
        masked_flag = "None"
    
    log_message = f"SUBMISSION - User:{user_id} - Challenge:{challenge_id} - Status:{status} - Flag:{masked_flag}"
    logger.info(log_message)

def log_admin_action(admin_id, action, target_type, target_id, details=None):
    """
    记录管理员操作
    
    Args:
        admin_id: 管理员ID
        action: 操作类型
        target_type: 目标类型
        target_id: 目标ID
        details: 详细信息
    """
    logger = current_app.logger
    
    log_message = f"ADMIN - User:{admin_id} - Action:{action} - Target:{target_type}:{target_id}"
    
    if details:
        log_message += f" - Details:{details}"
    
    logger.info(log_message)

def log_system_event(event_type, description, severity='INFO'):
    """
    记录系统事件
    
    Args:
        event_type: 事件类型
        description: 事件描述
        severity: 严重程度
    """
    logger = current_app.logger
    
    log_message = f"SYSTEM - {event_type} - {description}"
    
    if severity.upper() == 'CRITICAL':
        logger.critical(log_message)
    elif severity.upper() == 'ERROR':
        logger.error(log_message)
    elif severity.upper() == 'WARNING':
        logger.warning(log_message)
    else:
        logger.info(log_message)

class RequestLogger:
    """请求日志记录器"""
    
    def __init__(self, app=None):
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        @app.before_request
        def before_request():
            # 记录请求开始时间
            request.start_time = datetime.utcnow()
        
        @app.after_request
        def after_request(response):
            # 计算请求处理时间
            if hasattr(request, 'start_time'):
                processing_time = (datetime.utcnow() - request.start_time).total_seconds() * 1000
                
                # 记录请求日志（排除静态文件）
                if not request.path.startswith('/static/'):
                    current_app.logger.info(
                        f"REQUEST - {request.method} {request.path} - "
                        f"Status:{response.status_code} - "
                        f"Time:{processing_time:.2f}ms - "
                        f"IP:{request.remote_addr}"
                    )
            
            return response

# 创建全局日志记录器实例
request_logger = RequestLogger()