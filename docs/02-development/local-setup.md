# CTF平台本地开发环境搭建指南

## 1. 环境要求

### 1.1 系统要求

- **操作系统**: Windows 10/11, macOS 10.15+, Ubuntu 20.04+ 或其他 Linux 发行版
- **内存**: 至少 4GB RAM
- **存储**: 至少 2GB 可用空间
- **网络**: 需要访问互联网以下载依赖包

### 1.2 软件要求

- **Python**: 3.8 或更高版本
- **MySQL**: 5.7 或更高版本
- **Git**: 用于版本控制
- **Node.js** (可选): 用于前端开发工具

## 2. 环境搭建步骤

### 2.1 克隆项目代码

```
# 克隆项目到本地
git clone https://github.com/your-org/ctf-platform.git
cd ctf-platform

# 项目结构
ls -la
# backend/     # 后端代码
# frontend/    # 前端代码
# docs/        # 文档
# README.md    # 项目说明
```



### 2.2 安装后端依赖

#### Windows 用户

```
# 1. 安装Python (从官网下载)
# 访问 https://www.python.org/downloads/
# 安装时勾选 "Add Python to PATH"

# 2. 进入后端目录
cd backend

# 3. 创建虚拟环境
python -m venv venv

# 4. 激活虚拟环境
# 方法1: 使用PowerShell
venv\Scripts\Activate.ps1
# 方法2: 使用CMD
venv\Scripts\activate.bat

# 5. 安装依赖
pip install -r requirements.txt
```



#### macOS/Linux 用户

```
# 1. 检查Python版本
python3 --version

# 2. 进入后端目录
cd backend

# 3. 创建虚拟环境
python3 -m venv venv

# 4. 激活虚拟环境
source venv/bin/activate

# 5. 安装依赖
pip install -r requirements.txt
```



### 2.3 安装和配置MySQL

#### Windows 安装MySQL

```
# 1. 下载MySQL安装包
# 访问 https://dev.mysql.com/downloads/installer/

# 2. 运行安装程序
# 选择 "Developer Default" 安装类型
# 记住设置的root密码

# 3. 启动MySQL服务
# 方法1: 使用服务管理器
# 按 Win + R, 输入 "services.msc"
# 找到 "MySQL80" 服务并启动

# 方法2: 使用命令行
net start MySQL80
```



#### macOS 安装MySQL

```
# 方法1: 使用Homebrew
brew install mysql
brew services start mysql

# 方法2: 下载DMG安装包
# 访问 https://dev.mysql.com/downloads/mysql/
```



#### Linux (Ubuntu/Debian) 安装MySQL

```
# 1. 更新包列表
sudo apt update

# 2. 安装MySQL
sudo apt install mysql-server

# 3. 启动MySQL服务
sudo systemctl start mysql
sudo systemctl enable mysql

# 4. 运行安全配置脚本
sudo mysql_secure_installation
```



### 2.4 配置数据库

#### 创建数据库和用户

```
-- 使用MySQL命令行工具
mysql -u root -p

-- 创建数据库
CREATE DATABASE ctf_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户
CREATE USER 'ctf_user'@'localhost' IDENTIFIED BY 'ctf_password';

-- 授予权限
GRANT ALL PRIVILEGES ON ctf_platform.* TO 'ctf_user'@'localhost';
FLUSH PRIVILEGES;

-- 退出
EXIT;
```



#### 测试数据库连接

```
# 测试连接
mysql -u ctf_user -p ctf_platform
# 输入密码: ctf_password
# 如果成功连接，显示 mysql> 提示符
```



### 2.5 配置应用环境变量

#### 创建配置文件

```
# 在后端目录创建 .env 文件
cd backend
touch .env
```



#### 编辑 .env 文件

```
# 应用配置
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production

# 数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=ctf_user
MYSQL_PASSWORD=ctf_password
MYSQL_DATABASE=ctf_platform

# Redis配置 (可选)
REDIS_URL=redis://localhost:6379/0

# 文件上传配置
MAX_CONTENT_LENGTH=16777216  # 16MB

# 平台配置
PLATFORM_NAME=CTF开发平台
PLATFORM_DESCRIPTION=本地开发环境
REGISTRATION_OPEN=true
REQUIRE_EMAIL_VERIFICATION=false

# 安全配置 (开发环境可关闭)
RATE_LIMITING_ENABLED=false

# 邮件配置 (开发环境可选)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-specific-password
```



### 2.6 初始化数据库

#### 运行初始化脚本

```
# 确保在backend目录，且虚拟环境已激活
cd backend
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 运行初始化脚本
python init_database.py
```



#### 或使用Flask命令

```
# 设置环境变量
export FLASK_APP=app.py  # Linux/macOS
# 或 set FLASK_APP=app.py  # Windows

# 初始化数据库
flask init-db
```



#### 验证数据库初始化

```
# 连接到MySQL查看创建的表
mysql -u ctf_user -p ctf_platform -e "SHOW TABLES;"

# 应看到以下表：
# +-------------------------+
# | Tables_in_ctf_platform  |
# +-------------------------+
# | categories              |
# | challenges              |
# | submissions             |
# | system_logs             |
# | users                   |
# +-------------------------+

# 查看默认用户
mysql -u ctf_user -p ctf_platform -e "SELECT username, email, is_admin FROM users;"

# 应看到：
# +----------+-----------------------+----------+
# | username | email                 | is_admin |
# +----------+-----------------------+----------+
# | admin    | admin@ctfplatform.com |        1 |
# +----------+-----------------------+----------+
```



### 2.7 配置前端

#### 修改API配置

```
// 编辑 frontend/utils.js
// 修改 API_BASE 为后端服务地址
const API_BASE = 'http://localhost:5000/api/v1';
```



#### 启动前端开发服务器

```
# 方法1: 直接使用浏览器打开
# 直接双击打开 frontend/index.html

# 方法2: 使用Python简单HTTP服务器
cd frontend
python -m http.server 8000
# 或 python3 -m http.server 8000

# 方法3: 使用Node.js的http-server
npm install -g http-server
http-server -p 8000
```



### 2.8 启动后端服务

#### 开发模式启动

```
# 确保在backend目录，且虚拟环境已激活
cd backend
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 设置环境变量
export FLASK_ENV=development  # Linux/macOS
export FLASK_APP=app.py
# 或 set FLASK_ENV=development  # Windows
# 或 set FLASK_APP=app.py

# 启动开发服务器
flask run --host=0.0.0.0 --port=5000
# 或 python app.py
```



#### 验证后端服务

```
# 检查服务是否运行
curl http://localhost:5000/health
# 应返回JSON健康状态

curl http://localhost:5000/
# 应返回API欢迎信息
```



### 2.9 访问应用

#### 在浏览器中打开

1. **前端界面**: [http://localhost:8000](http://localhost:8000/) (或直接打开 index.html)
2. **后端API**: [http://localhost:5000](http://localhost:5000/)
3. **API文档**: http://localhost:5000/api/docs (如果配置了Swagger)

#### 测试登录

1. 访问 [http://localhost:8000](http://localhost:8000/)
2. 点击右上角 "登录"
3. 使用默认管理员账号:
   - 用户名: `admin`
   - 密码: `admin123`
4. 登录成功后应看到管理员菜单

## 3. 开发工作流

### 3.1 代码结构

```
ctf-platform/
├── backend/
│   ├── app.py              # Flask应用主文件
│   ├── config.py           # 配置文件
│   ├── models.py           # 数据模型
│   ├── requirements.txt    # Python依赖
│   ├── routes/             # 路由模块
│   │   ├── auth.py        # 认证路由
│   │   ├── challenges.py  # 题目路由
│   │   ├── submissions.py # 提交路由
│   │   ├── leaderboard.py # 排行榜路由
│   │   └── admin.py       # 管理员路由
│   ├── utils/             # 工具模块
│   │   ├── auth.py        # 认证工具
│   │   ├── flag.py        # Flag工具
│   │   ├── log.py         # 日志工具
│   │   └── scoring.py     # 计分工具
│   └── storage/           # 文件存储
│       ├── challenges/    # 题目附件
│       ├── temp/          # 临时文件
│       └── logs/          # 日志文件
├── frontend/
│   ├── index.html         # 主页面
│   ├── style.css          # 样式表
│   ├── utils.js           # 工具函数
│   ├── auth.js           # 认证模块
│   ├── challenges.js     # 题目模块
│   ├── leaderboard.js    # 排行榜模块
│   ├── admin.js          # 管理员模块
│   └── app.js            # 主应用逻辑
└── docs/                  # 文档
```



### 3.2 常用开发命令

#### 后端开发

```
# 激活虚拟环境
cd backend
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 运行开发服务器
flask run --host=0.0.0.0 --port=5000 --debug

# 运行测试
pytest

# 代码格式化
black .

# 代码检查
flake8

# 创建数据库迁移
flask db migrate -m "迁移描述"

# 应用数据库迁移
flask db upgrade
```



#### 前端开发

```
# 编辑前端文件
# frontend/ 目录下的 HTML、CSS、JS 文件

# 实时预览 (需要安装Live Server)
# VS Code插件: Live Server
# 右键 index.html -> Open with Live Server
```



### 3.3 创建测试数据

#### 使用Python交互环境

```
cd backend
source venv/bin/activate
python

# 在Python交互环境中
>>> from app import create_app
>>> from models import db, User, Challenge, Category
>>> app = create_app()
>>> with app.app_context():
...     # 创建测试用户
...     user = User(username='testuser', email='test@example.com')
...     user.set_password('test123')
...     db.session.add(user)
...     
...     # 创建测试题目
...     category = Category(name='测试分类', description='测试用分类')
...     db.session.add(category)
...     db.session.commit()
...     
...     challenge = Challenge(
...         title='测试题目',
...         description='这是一个测试题目',
...         flag='CTF{test_flag_123}',
...         points=100,
...         difficulty='easy',
...         category_id=category.id,
...         creator_id=1
...     )
...     db.session.add(challenge)
...     db.session.commit()
...     print('测试数据创建成功！')
```



#### 使用SQL插入数据

```
-- 插入测试用户
INSERT INTO users (username, email, password_hash, is_admin, score) 
VALUES ('testuser', 'test@example.com', 
'pbkdf2:sha256:260000$...', 0, 0);

-- 插入测试题目
INSERT INTO challenges (title, description, flag, points, difficulty, category_id, creator_id)
VALUES ('测试题目', '这是测试题目描述', 'CTF{test_flag}', 100, 'easy', 1, 1);
```



## 4. 常见问题排查

### 4.1 MySQL连接问题

#### 问题：连接被拒绝

```
错误：Can't connect to MySQL server on 'localhost' (10061)
```



**解决方案**：

```
# 1. 检查MySQL服务是否运行
# Windows
net start MySQL80

# Linux
sudo systemctl status mysql

# macOS
brew services list | grep mysql

# 2. 检查端口是否监听
netstat -an | grep 3306

# 3. 检查MySQL配置文件
# 编辑 /etc/mysql/my.cnf 或 /etc/my.cnf
# 确保有 bind-address = 127.0.0.1 或 0.0.0.0
```



#### 问题：用户权限不足

```
错误：Access denied for user 'ctf_user'@'localhost'
```



**解决方案**：

```
-- 使用root登录MySQL
mysql -u root -p

-- 重新创建用户和权限
DROP USER IF EXISTS 'ctf_user'@'localhost';
CREATE USER 'ctf_user'@'localhost' IDENTIFIED BY 'ctf_password';
GRANT ALL PRIVILEGES ON ctf_platform.* TO 'ctf_user'@'localhost';
FLUSH PRIVILEGES;
```



### 4.2 Python依赖问题

#### 问题：ModuleNotFoundError

```
错误：ModuleNotFoundError: No module named 'flask'
```



**解决方案**：

```
# 1. 检查虚拟环境是否激活
# Linux/macOS: 确保终端提示符前有 (venv)
# Windows: 确保提示符前有 (venv)

# 2. 重新安装依赖
pip install -r requirements.txt

# 3. 检查Python版本
python --version  # 应为3.8+
```



#### 问题：MySQL客户端安装失败

```
错误：Failed building wheel for mysqlclient
```



**解决方案**：

```
# Windows: 安装预编译包
pip install mysqlclient-1.4.6-cp38-cp38-win_amd64.whl
# 从 https://www.lfd.uci.edu/~gohlke/pythonlibs/#mysqlclient 下载对应版本

# Linux: 安装系统依赖
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential

# macOS: 使用Homebrew
brew install mysql-client
export PATH="/usr/local/opt/mysql-client/bin:$PATH"
```



### 4.3 端口冲突问题

#### 问题：端口已被占用

```
错误：Address already in use
```



**解决方案**：

```
# 1. 查找占用端口的进程
# Linux/macOS
lsof -i :5000
kill -9 <PID>

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# 2. 使用其他端口
flask run --port=5001
```



### 4.4 前端API请求失败

#### 问题：跨域请求被阻止

```
错误：Access to fetch at 'http://localhost:5000/api/v1/auth/login' from origin 'http://localhost:8000' has been blocked by CORS policy
```



**解决方案**：

1. 检查后端CORS配置：

```
# 确保 config.py 中有 CORS 配置
CORS(app, supports_credentials=True)
```



1. 检查前端API地址：

```
// 确保 utils.js 中的 API_BASE 正确
const API_BASE = 'http://localhost:5000/api/v1';
```



1. 在同一端口下运行前后端：

```
# 修改前端API地址为相对路径
const API_BASE = '/api/v1';

# 使用Nginx代理或修改后端服务前端文件
```



### 4.5 数据库迁移问题

#### 问题：迁移脚本冲突

```
错误：Target database is not up to date
```



**解决方案**：

```
# 1. 检查当前迁移状态
flask db current

# 2. 回滚到上一个版本
flask db downgrade

# 3. 重新生成迁移
flask db migrate -m "修复迁移"

# 4. 应用迁移
flask db upgrade
```



### 4.6 文件上传问题

#### 问题：文件上传失败

```
错误：RequestEntityTooLarge
```



**解决方案**：

1. 检查配置文件：

```
# 确保 .env 中有正确的文件大小限制
MAX_CONTENT_LENGTH=16777216  # 16MB
```



1. 检查Nginx配置（如果使用）：

```
client_max_body_size 16M;
```



1. 检查存储目录权限：

```
chmod -R 755 backend/storage/
chown -R $USER:$USER backend/storage/
```



## 5. 调试技巧

### 5.1 Flask调试模式

```
# 在 app.py 中启用调试
if __name__ == '__main__':
    app.run(debug=True)
```



### 5.2 打印调试信息

```
# 在代码中添加日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 或使用print
print(f"调试信息: {variable}")
```



### 5.3 使用VS Code调试

#### launch.json 配置

```
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Flask",
            "type": "python",
            "request": "launch",
            "module": "flask",
            "env": {
                "FLASK_APP": "app.py",
                "FLASK_ENV": "development"
            },
            "args": [
                "run",
                "--no-debugger",
                "--no-reload"
            ],
            "jinja": true,
            "justMyCode": true
        }
    ]
}
```



### 5.4 数据库调试

```
# 启用SQL查询日志
app.config['SQLALCHEMY_ECHO'] = True

# 或在查询时打印SQL
query = db.session.query(User).filter(User.id == 1)
print(str(query))
```



## 6. 性能优化建议

### 6.1 开发环境优化

```
# 禁用不必要的中间件
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 减少日志级别
app.logger.setLevel(logging.WARNING)

# 禁用缓存
app.config['CACHE_TYPE'] = 'null'
```



### 6.2 数据库优化

```
-- 为常用查询添加索引
CREATE INDEX idx_user_score ON users(score DESC);
CREATE INDEX idx_challenge_category ON challenges(category_id);
CREATE INDEX idx_submission_user_challenge ON submissions(user_id, challenge_id);
```



### 6.3 前端优化

```
// 禁用生产环境特性
if (window.location.hostname === 'localhost') {
    console.log('开发模式：启用调试功能');
    // 开发环境特定代码
}
```



## 7. 备份和恢复

### 7.1 备份开发数据

```
# 备份数据库
mysqldump -u ctf_user -p ctf_platform > backup_$(date +%Y%m%d).sql

# 备份文件
tar -czf storage_backup_$(date +%Y%m%d).tar.gz backend/storage/
```



### 7.2 恢复开发数据

```
# 恢复数据库
mysql -u ctf_user -p ctf_platform < backup_20240101.sql

# 恢复文件
tar -xzf storage_backup_20240101.tar.gz
```



## 8. 扩展开发环境

### 8.1 添加开发工具

```
# 安装开发依赖
pip install ipython  # 更好的Python交互环境
pip install ipdb     # 交互式调试器
pip install autopep8 # 自动格式化代码

# 创建开发专用的 requirements-dev.txt
echo "-r requirements.txt" > requirements-dev.txt
echo "ipython" >> requirements-dev.txt
echo "ipdb" >> requirements-dev.txt
echo "autopep8" >> requirements-dev.txt
```



### 8.2 配置开发脚本

```
# 创建开发启动脚本 dev.sh
#!/bin/bash
echo "启动CTF平台开发环境..."

# 激活虚拟环境
source venv/bin/activate

# 启动后端
echo "启动后端服务器..."
flask run --host=0.0.0.0 --port=5000 --debug &

# 启动前端服务器
echo "启动前端服务器..."
cd ../frontend
python -m http.server 8000 &

echo "开发环境已启动！"
echo "前端: http://localhost:8000"
echo "后端: http://localhost:5000"

# 等待所有进程
wait
```



### 8.3 配置开发数据库

```
-- 创建开发专用的数据库
CREATE DATABASE ctf_platform_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON ctf_platform_dev.* TO 'ctf_user'@'localhost';
```

------

**本地开发环境搭建完成！**

现在你可以：

1. 修改后端代码，重启Flask服务生效
2. 修改前端代码，刷新浏览器生效
3. 使用管理员账号登录测试功能
4. 创建测试数据和测试用例

如果遇到问题，请参考第4部分的常见问题排查，或查阅项目文档。