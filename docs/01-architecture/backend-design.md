# CTF平台后端设计文档

## 1. 后端架构概述

CTF平台后端基于Flask框架构建，采用模块化设计，提供RESTful API接口。系统设计注重安全性、性能和可扩展性。

## 2. 技术栈详解

### 2.1 核心框架

```
# requirements.txt 核心依赖
Flask==2.3.3            # Web框架
Flask-SQLAlchemy==3.0.5 # ORM
Flask-Migrate==4.0.5    # 数据库迁移
Flask-CORS==4.0.0       # 跨域支持
flask_login             # 用户会话管理
```

### 2.2 数据库驱动

```
PyMySQL==1.1.0          # MySQL Python驱动
mysqlclient==2.1.1      # 高性能MySQL连接
```

### 2.3 安全组件

```
PyJWT==2.8.0            # JWT令牌
Werkzeug==2.3.7         # WSGI工具集（包含密码哈希）
bcrypt==4.0.1           # 密码哈希算法
```

### 2.4 辅助组件

```
python-magic==0.4.27    # 文件类型检测
Flask-Mail==0.9.1       # 邮件支持
Redis==5.0.1            # 缓存
Flask-Caching==2.0.2    # 缓存集成
```

## 3. 模块划分

### 3.1 应用入口 (`app.py`)

```
# 主要职责：
# 1. 应用工厂模式创建Flask实例
# 2. 配置加载
# 3. 扩展初始化
# 4. 蓝图注册
# 5. 错误处理器注册
# 6. 命令行工具注册

def create_app(config_class=None):
    app = Flask(__name__)
    app.config.from_object(config_class or get_config())
    
    # 初始化扩展
    db.init_app(app)
    migrate = Migrate(app, db)
    CORS(app, supports_credentials=True)
    
    # 注册蓝图
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(challenges_bp, url_prefix='/api/v1')
    app.register_blueprint(submissions_bp, url_prefix='/api/v1')
    app.register_blueprint(leaderboard_bp, url_prefix='/api/v1')
    app.register_blueprint(admin_bp, url_prefix='/api/v1/admin')
    
    return app
```

### 3.2 配置管理 (`config.py`)

```
# 支持多环境配置
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# 环境变量驱动配置
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{user}:{pass}@{host}:{port}/{db}'
    # 更多配置项...
```

### 3.3 数据库模型 (`models.py`)

```
# 核心数据模型
class User(db.Model, UserMixin):
    # 用户表：存储用户信息和认证数据
    __tablename__ = 'users'
    
class Category(db.Model):
    # 分类表：题目分类
    __tablename__ = 'categories'
    
class Challenge(db.Model):
    # 题目表：存储题目信息
    __tablename__ = 'challenges'
    
class Submission(db.Model):
    # 提交记录表：存储Flag提交记录
    __tablename__ = 'submissions'
    
class SystemLog(db.Model):
    # 系统日志表：审计和安全日志
    __tablename__ = 'system_logs'
```

### 3.4 路由模块 (`routes/`)

```
routes/
├── auth.py           # 认证相关路由
├── admin.py          # 管理员路由
├── challenges.py     # 题目相关路由
├── submissions.py    # 提交记录路由
└── leaderboard.py    # 排行榜路由
```

### 3.5 工具模块 (`utils/`)

```
utils/
├── auth.py          # JWT认证工具
├── flag.py          # Flag生成和验证
├── log.py           # 日志系统
└── scoring.py       # 计分系统
```

## 4. 数据库设计

### 4.1 数据库ER图

![ER图](docs/images/uml/ER图.png)

### 4.2 数据关系

```
users (1) -- (N) submissions
users (1) -- (N) challenges (作为创建者)
users (0..1) -- (N) challenges (作为一血获得者)
categories (1) -- (N) challenges
challenges (1) -- (N) submissions
```

### 4.3 索引优化策略

1. **查询频率高的字段添加索引**：

   - `users.username`, `users.email`
   - `challenges.title`, `challenges.category_id`
   - `submissions.user_id`, `submissions.challenge_id`

2. **复合索引优化关联查询**：

   ```
   -- 用户提交记录查询优化
   CREATE INDEX idx_user_challenge ON submissions(user_id, challenge_id, submitted_at DESC);
   
   -- 排行榜查询优化
   CREATE INDEX idx_user_score ON users(score DESC, created_at);
   ```

## 5. API设计

### 5.1 RESTful API规范

- **版本控制**: `/api/v1/`
- **资源命名**: 使用复数名词 (`/challenges`, `/users`)
- **HTTP方法**:
  - GET: 获取资源
  - POST: 创建资源
  - PUT: 更新资源
  - DELETE: 删除资源
- **状态码**: 标准化HTTP状态码
- **错误响应**: 统一错误格式

### 5.2 主要API端点

#### 认证API (`/api/v1/auth`)

```
POST /auth/register     # 用户注册
POST /auth/login        # 用户登录
GET  /auth/profile      # 获取用户信息
PUT  /auth/profile      # 更新用户信息
```

#### 题目API (`/api/v1`)

```
GET    /challenges                  # 获取题目列表
GET    /challenges/{id}             # 获取题目详情
POST   /challenges                  # 创建题目（管理员）
PUT    /challenges/{id}             # 更新题目（管理员）
DELETE /challenges/{id}             # 删除题目（管理员）
POST   /challenges/{id}/submit      # 提交Flag
GET    /challenges/{id}/download    # 下载附件
GET    /categories                  # 获取分类列表
```

#### 排行榜API (`/api/v1`)

```
GET /leaderboard                    # 全球排行榜
GET /leaderboard/category/{id}      # 分类排行榜
GET /leaderboard/challenge/{id}     # 题目排行榜
```

#### 管理员API (`/api/v1/admin`)

```
GET    /admin/stats                 # 平台统计
GET    /admin/users                 # 用户列表
PUT    /admin/users/{id}            # 更新用户
DELETE /admin/users/{id}            # 删除用户
GET    /admin/submissions           # 提交记录
POST   /admin/categories            # 创建分类
PUT    /admin/categories/{id}       # 更新分类
DELETE /admin/categories/{id}       # 删除分类
POST   /admin/update-scores         # 更新分数
GET    /admin/export-data           # 导出数据
```

### 5.3 API响应格式

```
{
  "success": true,
  "message": "操作成功",
  "data": {
    // 实际数据
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 6. 安全设计

### 6.1 认证安全

```
# JWT令牌验证装饰器
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        # 验证逻辑...
    return decorated

# 管理员权限验证装饰器
def admin_required(f):
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_admin:
            return jsonify({'message': 'Admin access required!'}), 403
        return f(current_user, *args, **kwargs)
    return decorated
```

### 6.2 数据验证

```
# 输入数据验证
def validate_challenge_data(data):
    required_fields = ['title', 'description', 'flag', 'points', 'difficulty', 'category_id']
    # 验证必填字段
    # 验证数据类型
    # 验证业务规则
```

### 6.3 请求限制

```
# 频率限制配置
RATE_LIMITING_ENABLED = True
MAX_SUBMISSIONS_PER_MINUTE = 30  # 生产环境可降低到10
```

## 7. 性能优化

### 7.1 数据库优化

```
# SQLAlchemy连接池配置
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_recycle': 300,      # 连接回收时间
    'pool_pre_ping': True,    # 连接前ping检测
    'pool_size': 20,          # 连接池大小
    'max_overflow': 30        # 最大溢出连接数
}
```

### 7.2 缓存策略

```
# Redis缓存配置
REDIS_URL = 'redis://localhost:6379/0'

# 缓存装饰器示例
@cache.cached(timeout=300, key_prefix='challenges_list')
def get_challenges():
    return Challenge.query.filter_by(is_hidden=False).all()
```

### 7.3 查询优化

```
# 使用join优化查询
def get_leaderboard_data():
    return db.session.query(
        User.id,
        User.username,
        User.score,
        func.count(distinct(Submission.challenge_id)).label('solved_count')
    ).outerjoin(
        Submission, (User.id == Submission.user_id) & (Submission.is_correct == True)
    ).group_by(User.id).order_by(User.score.desc()).all()
```

## 8. 错误处理

### 8.1 全局错误处理器

```
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
```

### 8.2 业务异常处理

```
class CTFException(Exception):
    """CTF平台基础异常类"""
    def __init__(self, message, code=400):
        self.message = message
        self.code = code
        
class FlagVerificationError(CTFException):
    """Flag验证异常"""
    pass

class RateLimitExceeded(CTFException):
    """频率限制异常"""
    def __init__(self, message='Rate limit exceeded', code=429):
        super().__init__(message, code)
```

## 9. 日志系统

### 9.1 日志配置

```
def setup_logging(app):
    """设置日志配置"""
    # 文件处理器（按大小轮转）
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=1024 * 1024 * 10,  # 10MB
        backupCount=10
    )
    
    # 日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
```

### 9.2 日志分类

- **安全日志**: 记录认证、授权、敏感操作
- **业务日志**: 记录用户操作、Flag提交
- **系统日志**: 记录系统事件、错误信息
- **审计日志**: 记录管理员操作

## 10. 部署与维护

### 10.1 环境配置

```
# .env 配置文件示例
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=ctf_user
MYSQL_PASSWORD=your-password
MYSQL_DATABASE=ctf_platform
REDIS_URL=redis://localhost:6379/0
```

### 10.2 初始化脚本

```
# init_database.py - 数据库初始化
def main():
    app = create_app()
    with app.app_context():
        init_db(app)  # 创建表结构
        # 创建默认分类
        # 创建管理员用户
```

### 10.3 命令行工具

```
# Flask CLI命令
@app.cli.command('init-db')
def init_database():
    """初始化数据库"""
    
@app.cli.command('create-admin')
def create_admin():
    """创建管理员用户"""
    
@app.cli.command('update-scores')
def update_scores():
    """更新题目动态分数"""
    
@app.cli.command('export-data')
def export_data():
    """导出平台数据"""
```

## 11. 扩展性设计

### 11.1 插件机制

```
# 插件注册接口
class PluginRegistry:
    def __init__(self):
        self.plugins = {}
    
    def register(self, name, plugin):
        self.plugins[name] = plugin
```

### 11.2 WebHook支持

```
# WebHook处理器
class WebHookHandler:
    def trigger(self, event_type, data):
        for hook in self.hooks.get(event_type, []):
            requests.post(hook.url, json=data)
```

## 12. 监控指标

### 12.1 性能指标

- API响应时间
- 数据库查询性能
- 内存使用率
- CPU使用率

### 12.2 业务指标

- 活跃用户数
- 题目解决率
- Flag提交成功率
- 排行榜更新频率

------

**后端设计总结**：

1. **架构清晰**: 模块化设计，职责分离
2. **安全性强**: 多层次安全防护
3. **性能优良**: 数据库优化 + 缓存策略
4. **易于维护**: 完善的日志和错误处理
5. **可扩展**: 插件化设计和WebHook支持
6. **标准化**: RESTful API设计，符合行业标准