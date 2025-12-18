# CTF平台部署架构文档

## 1. 部署架构概述

CTF平台采用传统的服务器部署架构，不依赖容器化技术。系统支持多环境部署（开发、测试、生产），数据库使用MySQL，缓存可选Redis。

## 2. 环境划分

### 2.1 开发环境 (Development)

- **目的**: 本地开发和调试
- **特点**: 宽松的安全限制，详细的日志，热重载
- **数据库**: 本地MySQL实例
- **配置**: `FLASK_ENV=development`

### 2.2 测试环境 (Testing)

- **目的**: 功能测试和集成测试
- **特点**: 独立的测试数据库，禁用生产安全限制
- **数据库**: 独立的MySQL测试数据库
- **配置**: `FLASK_ENV=testing`

### 2.3 生产环境 (Production)

- **目的**: 线上服务
- **特点**: 严格的安全配置，性能优化，监控
- **数据库**: 生产MySQL集群
- **配置**: `FLASK_ENV=production`

## 3. 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                         用户端                                │
│                    (浏览器/移动端)                            │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTPS
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                       Web服务器                               │
│                      (Nginx/Apache)                          │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │                  反向代理配置                         │     │
│  │  location /api {                                   │     │
│  │      proxy_pass http://127.0.0.1:5000;            │     │
│  │      proxy_set_header Host $host;                 │     │
│  │      proxy_set_header X-Real-IP $remote_addr;     │     │
│  │  }                                                │     │
│  │                                                   │     │
│  │  location / {                                     │     │
│  │      root /var/www/ctf-frontend;                  │     │
│  │      try_files $uri $uri/ /index.html;            │     │
│  │  }                                                │     │
│  └────────────────────────────────────────────────────┘     │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    应用服务器                                 │
│                   (Flask + Gunicorn)                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Worker 1 │  │ Worker 2 │  │ Worker 3 │  │ Worker 4 │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │                   Supervisor                       │     │
│  │  管理Gunicorn进程和自动重启                        │     │
│  └────────────────────────────────────────────────────┘     │
└────────────────────────────┬────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌───────────────┐  ┌───────────────┐  ┌─────────────────────┐
│   MySQL主库   │  │   缓存服务器   │  │    文件存储系统      │
│               │  │   (Redis)     │  │   (本地/NFS)        │
└───────────────┘  └───────────────┘  └─────────────────────┘
        │
        ▼
┌───────────────┐
│   MySQL从库   │
│   (可选)      │
└───────────────┘
```



## 4. 服务器配置

### 4.1 系统要求

#### 最低配置

```
生产环境:
  CPU: 4核心
  内存: 8GB
  存储: 100GB SSD
  操作系统: Ubuntu 20.04 LTS / CentOS 8

测试环境:
  CPU: 2核心
  内存: 4GB
  存储: 50GB SSD

开发环境:
  本地机器即可
```



#### 推荐配置

```
生产环境:
  CPU: 8核心
  内存: 16GB
  存储: 200GB SSD + 1TB HDD (备份)
  带宽: 100Mbps
```



### 4.2 软件依赖

#### 系统包

```
# Ubuntu/Debian
apt-get update
apt-get install -y \
  python3.9 python3.9-dev python3-pip \
  mysql-server mysql-client \
  nginx \
  supervisor \
  redis-server \
  git \
  build-essential \
  libssl-dev libffi-dev \
  libmysqlclient-dev
```



#### Python依赖

bash

```
# 通过requirements.txt安装
pip3 install -r requirements.txt
```



## 5. 数据库部署

### 5.1 MySQL配置

#### 基础配置 (`/etc/mysql/my.cnf`)

```
[mysqld]
# 基础配置
datadir = /var/lib/mysql
socket = /var/run/mysqld/mysqld.sock
pid-file = /var/run/mysqld/mysqld.pid

# 字符集
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

# 连接配置
max_connections = 500
max_connect_errors = 1000
connect_timeout = 10
wait_timeout = 28800
interactive_timeout = 28800

# 内存配置
key_buffer_size = 256M
max_allowed_packet = 64M
thread_cache_size = 8
sort_buffer_size = 4M
read_buffer_size = 2M
read_rnd_buffer_size = 4M
join_buffer_size = 4M

# InnoDB配置
innodb_buffer_pool_size = 2G
innodb_log_file_size = 512M
innodb_flush_log_at_trx_commit = 2
innodb_lock_wait_timeout = 50
innodb_file_per_table = 1

# 日志配置
log-error = /var/log/mysql/error.log
slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow.log
long_query_time = 2

# 二进制日志（主从复制）
server-id = 1
log_bin = /var/log/mysql/mysql-bin.log
expire_logs_days = 7
```



#### 用户和权限

```
-- 创建数据库
CREATE DATABASE ctf_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户
CREATE USER 'ctf_user'@'localhost' IDENTIFIED BY 'secure_password_here';
CREATE USER 'ctf_user'@'%' IDENTIFIED BY 'secure_password_here';

-- 授予权限
GRANT ALL PRIVILEGES ON ctf_platform.* TO 'ctf_user'@'localhost';
GRANT ALL PRIVILEGES ON ctf_platform.* TO 'ctf_user'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, INDEX, ALTER, CREATE TEMPORARY TABLES, LOCK TABLES, EXECUTE ON ctf_platform.* TO 'ctf_user'@'%';

FLUSH PRIVILEGES;
```



### 5.2 数据库初始化

```
# 使用初始化脚本
python3 init_database.py

# 或使用Flask命令
flask init-db
```



## 6. 应用部署

### 6.1 项目结构

```
/var/www/ctf-platform/
├── backend/                 # 后端代码
│   ├── app.py
│   ├── config.py
│   ├── models.py
│   ├── requirements.txt
│   ├── storage/            # 文件存储
│   │   ├── challenges/
│   │   ├── temp/
│   │   └── logs/
│   └── venv/               # Python虚拟环境
├── frontend/               # 前端代码
│   ├── index.html
│   ├── style.css
│   ├── *.js
│   └── assets/             # 静态资源
├── nginx/                  # Nginx配置
├── supervisor/             # Supervisor配置
└── logs/                   # 应用日志
```



### 6.2 Gunicorn配置

#### 生产配置 (`gunicorn_config.py`)

```
# Gunicorn配置文件
import multiprocessing

# 绑定地址和端口
bind = "127.0.0.1:5000"

# 工作进程数
workers = multiprocessing.cpu_count() * 2 + 1

# 工作模式
worker_class = "sync"

# 日志配置
accesslog = "/var/log/ctf-platform/gunicorn_access.log"
errorlog = "/var/log/ctf-platform/gunicorn_error.log"
loglevel = "info"

# 进程名称
proc_name = "ctf_platform"

# 超时设置
timeout = 120
keepalive = 2

# 重启设置
max_requests = 1000
max_requests_jitter = 50

# 安全设置
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190
```



#### 启动脚本 (`start_gunicorn.sh`)

```
#!/bin/bash
cd /var/www/ctf-platform/backend
source venv/bin/activate

exec gunicorn \
    --config gunicorn_config.py \
    --log-level info \
    --access-logfile /var/log/ctf-platform/access.log \
    --error-logfile /var/log/ctf-platform/error.log \
    app:app
```



### 6.3 Supervisor配置

#### Supervisor配置 (`/etc/supervisor/conf.d/ctf-platform.conf`)

```
[program:ctf-platform]
directory=/var/www/ctf-platform/backend
command=/var/www/ctf-platform/backend/start_gunicorn.sh
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/ctf-platform/supervisor.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
stderr_logfile=/var/log/ctf-platform/supervisor_error.log
stderr_logfile_maxbytes=50MB
stderr_logfile_backups=10
environment=FLASK_ENV="production",PATH="/var/www/ctf-platform/backend/venv/bin"

[group:ctf]
programs=ctf-platform
```



#### Supervisor管理命令

```
# 重新加载配置
sudo supervisorctl reread
sudo supervisorctl update

# 管理服务
sudo supervisorctl start ctf-platform
sudo supervisorctl stop ctf-platform
sudo supervisorctl restart ctf-platform
sudo supervisorctl status ctf-platform
```



## 7. Web服务器配置

### 7.1 Nginx配置

#### 主配置文件 (`/etc/nginx/nginx.conf`)

```
user www-data;
worker_processes auto;
pid /run/nginx.pid;
error_log /var/log/nginx/error.log;
events {
    worker_connections 1024;
    multi_accept on;
    use epoll;
}
http {
    # 基础设置
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;
    
    # MIME类型
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    access_log /var/log/nginx/access.log main;
    
    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript 
               application/javascript application/x-javascript 
               application/xml application/json;
    
    # 站点配置
    include /etc/nginx/sites-enabled/*;
}
```



#### 站点配置 (`/etc/nginx/sites-available/ctf-platform`)

```
upstream ctf_backend {
    server 127.0.0.1:5000;
    keepalive 32;
}

server {
    listen 80;
    server_name ctf.example.com;
    
    # 强制HTTPS重定向
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name ctf.example.com;
    
    # SSL证书配置
    ssl_certificate /etc/ssl/certs/ctf.example.com.crt;
    ssl_certificate_key /etc/ssl/private/ctf.example.com.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # 安全头部
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;" always;
    
    # 前端静态文件
    location / {
        root /var/www/ctf-platform/frontend;
        index index.html;
        try_files $uri $uri/ /index.html;
        
        # 静态文件缓存
        location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # API反向代理
    location /api/ {
        proxy_pass http://ctf_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket支持（如果需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # 文件上传大小限制
    client_max_body_size 16M;
    
    # 访问日志
    access_log /var/log/nginx/ctf-platform-access.log;
    error_log /var/log/nginx/ctf-platform-error.log;
}
```



### 7.2 Apache配置（备选方案）

#### VirtualHost配置

```
<VirtualHost *:80>
    ServerName ctf.example.com
    ServerAdmin webmaster@example.com
    
    # 重定向到HTTPS
    Redirect permanent / https://ctf.example.com/
</VirtualHost>

<VirtualHost *:443>
    ServerName ctf.example.com
    DocumentRoot /var/www/ctf-platform/frontend
    
    # SSL配置
    SSLEngine on
    SSLCertificateFile /etc/ssl/certs/ctf.example.com.crt
    SSLCertificateKeyFile /etc/ssl/private/ctf.example.com.key
    
    # API代理
    ProxyPreserveHost On
    ProxyPass /api http://127.0.0.1:5000/api
    ProxyPassReverse /api http://127.0.0.1:5000/api
    
    # 前端文件
    <Directory /var/www/ctf-platform/frontend>
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>
    
    ErrorLog ${APACHE_LOG_DIR}/ctf-error.log
    CustomLog ${APACHE_LOG_DIR}/ctf-access.log combined
</VirtualHost>
```



## 8. 环境配置文件

### 8.1 环境变量配置 (`.env`)

```
# 环境类型
FLASK_ENV=production

# 应用密钥
SECRET_KEY=your-secret-key-here-change-in-production

# 数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=ctf_user
MYSQL_PASSWORD=secure_password_here
MYSQL_DATABASE=ctf_platform

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 邮件配置
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-specific-password

# 平台配置
PLATFORM_NAME=CTF平台
PLATFORM_DESCRIPTION=网络安全竞赛平台
REGISTRATION_OPEN=true
REQUIRE_EMAIL_VERIFICATION=false

# 安全配置
RATE_LIMITING_ENABLED=true
MAX_SUBMISSIONS_PER_MINUTE=10

# 文件上传
MAX_CONTENT_LENGTH=16777216  # 16MB

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=/var/log/ctf-platform/ctf_platform.log
```



### 8.2 多环境配置脚本

#### 环境检测脚本 (`check_environment.sh`)

```
#!/bin/bash

# 检查系统环境
echo "=== 环境检查 ==="
echo "当前用户: $(whoami)"
echo "主机名: $(hostname)"
echo "系统: $(uname -a)"
echo "Python版本: $(python3 --version)"
echo "Pip版本: $(pip3 --version)"
echo "MySQL版本: $(mysql --version 2>/dev/null || echo '未安装')"
echo "Nginx版本: $(nginx -v 2>&1 | head -1)"
echo "Redis版本: $(redis-server --version 2>/dev/null || echo '未安装')"

# 检查服务状态
echo -e "\n=== 服务状态 ==="
systemctl status mysql --no-pager | head -5
systemctl status nginx --no-pager | head -5
systemctl status redis-server --no-pager | head -5
systemctl status supervisor --no-pager | head -5

# 检查端口
echo -e "\n=== 端口监听 ==="
netstat -tlnp | grep -E ':80|:443|:3306|:6379|:5000' | sort

# 检查目录权限
echo -e "\n=== 目录权限 ==="
ls -ld /var/www/ctf-platform/
ls -ld /var/log/ctf-platform/
ls -ld /var/www/ctf-platform/backend/storage/

echo -e "\n环境检查完成！"
```



## 9. 部署脚本

### 9.1 自动化部署脚本 (`deploy.sh`)

```
#!/bin/bash
set -e

# 部署配置
DEPLOY_DIR="/var/www/ctf-platform"
BACKEND_DIR="$DEPLOY_DIR/backend"
FRONTEND_DIR="$DEPLOY_DIR/frontend"
BRANCH="main"
ENV="production"

echo "=== CTF平台部署脚本 ==="
echo "部署目录: $DEPLOY_DIR"
echo "环境: $ENV"
echo "分支: $BRANCH"

# 1. 备份当前版本
echo -e "\n1. 备份当前版本..."
if [ -d "$DEPLOY_DIR" ]; then
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_DIR="/var/backup/ctf-platform/$TIMESTAMP"
    mkdir -p $BACKUP_DIR
    cp -r $DEPLOY_DIR/* $BACKUP_DIR/ 2>/dev/null || true
    echo "备份到: $BACKUP_DIR"
fi

# 2. 拉取代码
echo -e "\n2. 拉取代码..."
if [ ! -d "$DEPLOY_DIR" ]; then
    git clone https://github.com/your-org/ctf-platform.git $DEPLOY_DIR
fi

cd $DEPLOY_DIR
git fetch origin
git checkout $BRANCH
git reset --hard origin/$BRANCH
git pull

# 3. 部署后端
echo -e "\n3. 部署后端..."
cd $BACKEND_DIR

# 创建虚拟环境
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 创建必要的目录
mkdir -p storage/challenges storage/temp storage/logs
chown -R www-data:www-data storage/
chmod -R 755 storage/

# 复制环境配置文件
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "请编辑 .env 文件配置环境变量"
fi

# 数据库迁移
flask db upgrade

# 4. 部署前端
echo -e "\n4. 部署前端..."
cd $FRONTEND_DIR

# 更新前端配置文件
sed -i "s|http://localhost:5000|https://$(hostname)|g" *.js

# 5. 重启服务
echo -e "\n5. 重启服务..."
supervisorctl restart ctf-platform
nginx -t && nginx -s reload

# 6. 健康检查
echo -e "\n6. 健康检查..."
sleep 5
curl -f https://$(hostname)/health || echo "健康检查失败"

echo -e "\n✅ 部署完成！"
echo "访问地址: https://$(hostname)"
```



### 9.2 回滚脚本 (`rollback.sh`)

```
#!/bin/bash
set -e

BACKUP_DIR="/var/backup/ctf-platform"
DEPLOY_DIR="/var/www/ctf-platform"

echo "=== CTF平台回滚脚本 ==="

# 列出可用的备份
echo "可用的备份:"
ls -1t $BACKUP_DIR | head -10

read -p "请输入要回滚的备份目录名: " BACKUP_NAME

if [ ! -d "$BACKUP_DIR/$BACKUP_NAME" ]; then
    echo "错误: 备份目录不存在"
    exit 1
fi

echo -e "\n回滚到备份: $BACKUP_NAME"

# 停止服务
echo -e "\n1. 停止服务..."
supervisorctl stop ctf-platform

# 恢复备份
echo -e "\n2. 恢复备份..."
rm -rf $DEPLOY_DIR
cp -r "$BACKUP_DIR/$BACKUP_NAME" $DEPLOY_DIR

# 重启服务
echo -e "\n3. 重启服务..."
supervisorctl start ctf-platform

echo -e "\n✅ 回滚完成！"
```



## 10. 备份策略

### 10.1 数据库备份脚本 (`backup_mysql.sh`)

```
#!/bin/bash
set -e

# 备份配置
BACKUP_DIR="/var/backup/mysql"
DB_NAME="ctf_platform"
DB_USER="ctf_user"
DB_PASS="secure_password_here"
RETENTION_DAYS=30

echo "=== MySQL数据库备份 ==="
echo "数据库: $DB_NAME"
echo "备份目录: $BACKUP_DIR"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 生成备份文件名
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.sql.gz"

# 执行备份
echo -e "\n开始备份..."
mysqldump -u$DB_USER -p$DB_PASS --single-transaction --routines --triggers $DB_NAME | gzip > $BACKUP_FILE

# 检查备份是否成功
if [ $? -eq 0 ]; then
    BACKUP_SIZE=$(du -h $BACKUP_FILE | cut -f1)
    echo "备份成功: $BACKUP_FILE ($BACKUP_SIZE)"
else
    echo "备份失败！"
    exit 1
fi

# 清理旧备份
echo -e "\n清理旧备份..."
find $BACKUP_DIR -name "${DB_NAME}_*.sql.gz" -mtime +$RETENTION_DAYS -delete

# 备份统计
BACKUP_COUNT=$(ls -1 $BACKUP_DIR/${DB_NAME}_*.sql.gz 2>/dev/null | wc -l)
echo -e "\n备份完成！"
echo "当前备份数量: $BACKUP_COUNT"
echo "备份目录: $BACKUP_DIR"
```



### 10.2 文件备份脚本 (`backup_files.sh`)

```
#!/bin/bash
set -e

# 备份配置
SOURCE_DIR="/var/www/ctf-platform"
BACKUP_DIR="/var/backup/files"
RETENTION_DAYS=7

echo "=== 文件系统备份 ==="
echo "源目录: $SOURCE_DIR"
echo "备份目录: $BACKUP_DIR"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 生成备份文件名
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/ctf_platform_${TIMESTAMP}.tar.gz"

# 排除不必要的文件
echo -e "\n开始备份..."
tar -czf $BACKUP_FILE \
    --exclude="*.pyc" \
    --exclude="__pycache__" \
    --exclude=".git" \
    --exclude="venv" \
    --exclude="storage/temp/*" \
    --exclude="storage/logs/*.log" \
    -C $SOURCE_DIR .

# 检查备份是否成功
if [ $? -eq 0 ]; then
    BACKUP_SIZE=$(du -h $BACKUP_FILE | cut -f1)
    echo "备份成功: $BACKUP_FILE ($BACKUP_SIZE)"
else
    echo "备份失败！"
    exit 1
fi

# 清理旧备份
echo -e "\n清理旧备份..."
find $BACKUP_DIR -name "ctf_platform_*.tar.gz" -mtime +$RETENTION_DAYS -delete

# 备份统计
BACKUP_COUNT=$(ls -1 $BACKUP_DIR/ctf_platform_*.tar.gz 2>/dev/null | wc -l)
echo -e "\n备份完成！"
echo "当前备份数量: $BACKUP_COUNT"
```



## 11. 监控与日志

### 11.1 日志管理

#### 日志轮转配置 (`/etc/logrotate.d/ctf-platform`)

```
/var/log/ctf-platform/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        supervisorctl signal USR1 ctf-platform
    endscript
}
```



### 11.2 监控脚本

#### 健康检查脚本 (`health_check.sh`)

```
#!/bin/bash

# 健康检查配置
URL="https://ctf.example.com"
EMAIL="admin@example.com"
LOG_FILE="/var/log/ctf-platform/health_check.log"

echo "$(date) - 开始健康检查" >> $LOG_FILE

# 1. 检查HTTP服务
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$URL/health")
if [ "$HTTP_STATUS" != "200" ]; then
    echo "$(date) - HTTP服务异常: $HTTP_STATUS" >> $LOG_FILE
    echo "HTTP服务异常: $HTTP_STATUS" | mail -s "CTF平台告警" $EMAIL
fi

# 2. 检查数据库连接
DB_CHECK=$(mysql -uctf_user -psecure_password_here -e "SELECT 1" ctf_platform 2>&1)
if [ $? -ne 0 ]; then
    echo "$(date) - 数据库连接异常: $DB_CHECK" >> $LOG_FILE
    echo "数据库连接异常" | mail -s "CTF平台告警" $EMAIL
fi

# 3. 检查磁盘空间
DISK_USAGE=$(df /var/www | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "$(date) - 磁盘空间不足: $DISK_USAGE%" >> $LOG_FILE
    echo "磁盘空间不足: $DISK_USAGE%" | mail -s "CTF平台告警" $EMAIL
fi

# 4. 检查内存使用
MEM_USAGE=$(free | grep Mem | awk '{print $3/$2 * 100.0}')
if [ $(echo "$MEM_USAGE > 80" | bc) -eq 1 ]; then
    echo "$(date) - 内存使用过高: $MEM_USAGE%" >> $LOG_FILE
    echo "内存使用过高: $MEM_USAGE%" | mail -s "CTF平台告警" $EMAIL
fi

echo "$(date) - 健康检查完成" >> $LOG_FILE
```



## 12. 安全加固

### 12.1 系统安全

```
# 1. 更新系统
apt-get update && apt-get upgrade -y

# 2. 配置防火墙
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow http
ufw allow https
ufw enable

# 3. 禁用root SSH登录
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
systemctl restart sshd

# 4. 安装fail2ban防止暴力破解
apt-get install fail2ban -y
cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
```



### 12.2 应用安全

```
# 1. 设置文件权限
chown -R www-data:www-data /var/www/ctf-platform
chmod -R 755 /var/www/ctf-platform
chmod -R 600 /var/www/ctf-platform/backend/.env

# 2. 配置SELinux/AppArmor
# 根据具体系统配置安全模块

# 3. 定期更新依赖
cd /var/www/ctf-platform/backend
source venv/bin/activate
pip list --outdated | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 pip install -U
```



## 13. 故障排除

### 13.1 常见问题

#### 问题1: 数据库连接失败

```
# 检查MySQL服务状态
systemctl status mysql

# 检查MySQL日志
tail -f /var/log/mysql/error.log

# 检查用户权限
mysql -uroot -p -e "SHOW GRANTS FOR 'ctf_user'@'localhost';"
```



#### 问题2: 应用启动失败

```
# 检查Supervisor日志
tail -f /var/log/ctf-platform/supervisor.log

# 检查应用日志
tail -f /var/log/ctf-platform/error.log

# 手动启动测试
cd /var/www/ctf-platform/backend
source venv/bin/activate
python app.py
```



#### 问题3: 文件上传失败

```
# 检查文件权限
ls -la /var/www/ctf-platform/backend/storage/

# 检查磁盘空间
df -h /var/www

# 检查Nginx上传限制
nginx -T | grep client_max_body_size
```



### 13.2 紧急恢复步骤

```
# 1. 停止服务
supervisorctl stop ctf-platform

# 2. 备份当前状态
cp -r /var/www/ctf-platform /var/backup/ctf-platform_emergency_$(date +%s)

# 3. 查看错误日志
tail -100 /var/log/ctf-platform/error.log

# 4. 临时修复（根据具体错误）
# ...

# 5. 重启服务
supervisorctl start ctf-platform

# 6. 验证服务
curl -f https://ctf.example.com/health
```



------

**部署架构总结**：

1. **简单可靠**: 不依赖容器化，使用成熟的Web服务器和进程管理
2. **可扩展**: 支持水平扩展（增加应用服务器实例）
3. **高可用**: 数据库主从复制（可选），负载均衡支持
4. **安全性高**: 多层次安全防护，定期备份
5. **易于维护**: 完整的部署和监控脚本
6. **成本可控**: 使用开源技术栈，硬件要求适中

该部署方案适合中小型CTF比赛，可以根据实际需求调整配置。对于大型比赛，可以考虑添加更多应用服务器和数据库从库来实现负载均衡。