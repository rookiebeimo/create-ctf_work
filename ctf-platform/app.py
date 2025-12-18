from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_migrate import Migrate
import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import get_config
from models import db, init_db
from utils.log import setup_logging, request_logger
from utils.auth import token_required

# 导入路由蓝图
from routes.auth import auth_bp
from routes.challenges import challenges_bp
from routes.submissions import submissions_bp
from routes.leaderboard import leaderboard_bp
from routes.admin import admin_bp

def create_app(config_class=None):
    """创建Flask应用工厂函数"""
    
    app = Flask(__name__)
    
    # 加载配置
    if config_class is None:
        config_class = get_config()
    app.config.from_object(config_class)
    
    # 初始化扩展
    db.init_app(app)
    migrate = Migrate(app, db)
    CORS(app, supports_credentials=True)
    
    # 设置日志
    setup_logging(app)
    request_logger.init_app(app)
    
    # 创建必要的目录
    create_directories(app)
    
    # 注册错误处理器
    register_error_handlers(app)
    
    # 注册路由蓝图
    register_blueprints(app)
    
    # 注册命令行命令
    register_commands(app)
    
    return app

def create_directories(app):
    """创建必要的目录"""
    directories = [
        app.config['UPLOAD_FOLDER'],
        app.config['CHALLENGE_ATTACHMENTS_FOLDER'],
        app.config['TEMP_FOLDER'],
        os.path.join(app.config['UPLOAD_FOLDER'], 'logs')
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def register_blueprints(app):
    """注册路由蓝图"""
    
    # API路由前缀
    api_prefix = '/api/v1'
    
    # 注册蓝图
    app.register_blueprint(auth_bp, url_prefix=f'{api_prefix}/auth')
    app.register_blueprint(challenges_bp, url_prefix=f'{api_prefix}')
    app.register_blueprint(submissions_bp, url_prefix=f'{api_prefix}')
    app.register_blueprint(leaderboard_bp, url_prefix=f'{api_prefix}')
    app.register_blueprint(admin_bp, url_prefix=f'{api_prefix}/admin')
    
    # 根路由
    @app.route('/')
    def index():
        return jsonify({
            'message': 'CTF Platform API',
            'version': '1.0.0',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    # 健康检查路由
    @app.route('/health')
    def health_check():
        try:
            # 测试数据库连接
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            db_status = 'healthy'
        except Exception as e:
            db_status = f'unhealthy: {str(e)}'
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': db_status
        })

def register_error_handlers(app):
    """注册错误处理器"""
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'message': 'Resource not found',
            'error': str(error)
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Internal Server Error: {str(error)}')
        return jsonify({
            'message': 'Internal server error',
            'error': 'An unexpected error occurred'
        }), 500
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'message': 'Forbidden',
            'error': str(error)
        }), 403
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'message': 'Unauthorized',
            'error': str(error)
        }), 401
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'message': 'Bad request',
            'error': str(error)
        }), 400

def register_commands(app):
    """注册命令行命令"""
    
    @app.cli.command('init-db')
    def init_database():
        """初始化数据库"""
        with app.app_context():
            init_db(app)
            print("数据库初始化完成！")
    
    @app.cli.command('create-admin')
    def create_admin():
        """创建管理员用户"""
        from models import User
        
        username = input("请输入管理员用户名: ")
        email = input("请输入管理员邮箱: ")
        password = input("请输入管理员密码: ")
        
        with app.app_context():
            if User.query.filter_by(username=username).first():
                print("用户已存在！")
                return
            
            admin_user = User(
                username=username,
                email=email,
                is_admin=True
            )
            admin_user.set_password(password)
            
            db.session.add(admin_user)
            db.session.commit()
            
            print(f"管理员用户 {username} 创建成功！")
    
    @app.cli.command('update-scores')
    def update_scores():
        """更新题目动态分数"""
        from utils.scoring import ScoringSystem
        
        with app.app_context():
            ScoringSystem.update_challenge_scores()
            print("题目分数更新完成！")
    
    @app.cli.command('export-data')
    def export_data():
        """导出平台数据"""
        import json
        from models import User, Challenge, Submission, Contest
        
        with app.app_context():
            data = {
                'export_time': datetime.utcnow().isoformat(),
                'users': [user.to_dict() for user in User.query.all()],
                'challenges': [challenge.to_dict() for challenge in Challenge.query.all()],
                'submissions': [submission.to_dict() for submission in Submission.query.limit(1000).all()]
            }
            
            export_file = f'ctf_export_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.json'
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"数据已导出到: {export_file}")

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    # 开发环境运行
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(
        host=os.environ.get('HOST', '0.0.0.0'),
        port=int(os.environ.get('PORT', 5000)),
        debug=debug_mode
    )