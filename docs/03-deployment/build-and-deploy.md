### Windows环境部署指南

```
# CTF平台 - Windows环境部署指南

## 📋 系统要求

### 硬件要求
- CPU: 双核以上
- 内存: 4GB以上
- 硬盘: 至少10GB可用空间
- 网络: 稳定的网络连接

### 软件要求
- **操作系统**: Windows 10/11 或 Windows Server 2016+
- **Python**: 3.8或更高版本
- **MySQL**: 8.0或更高版本
- **Git**: 版本控制工具（可选但推荐）

## 🔧 环境准备

### 1. 安装Python

1. 访问 [Python官网](https://www.python.org/downloads/)
2. 下载Python 3.8+ Windows安装包
3. 安装时务必勾选 **"Add Python to PATH"**
4. 验证安装：
   ```cmd
   python --version
   pip --version
```



### 2. 安装MySQL

1. 访问 [MySQL官网](https://dev.mysql.com/downloads/installer/)

2. 下载MySQL Installer for Windows

3. 选择"Developer Default"或"Server only"安装

4. 安装过程中：

   - 设置root密码（建议：`031006`或自定义）
   - 记住MySQL端口（默认3306）
   - 记下MySQL安装路径

5. 验证MySQL服务运行：

   ```
   # 以管理员身份运行CMD
   net start mysql
   ```

   

6. 可选：安装MySQL Workbench用于数据库管理

### 3. 配置MySQL数据库

1. 登录MySQL：

   ```
   mysql -u root -p
   ```

   

2. 创建数据库和用户：

   ```
   -- 创建数据库
   CREATE DATABASE ctf_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   
   -- 创建用户并授权
   CREATE USER 'ctf_user'@'localhost' IDENTIFIED BY '031006';
   GRANT ALL PRIVILEGES ON ctf_platform.* TO 'ctf_user'@'localhost';
   FLUSH PRIVILEGES;
   
   -- 验证用户
   USE mysql;
   SELECT user, host FROM user;
   ```

   

3. 退出MySQL：

   ```
   EXIT;
   ```

   

## 📦 项目部署

### 1. 获取项目代码

**方式一：Git克隆**

```
# 创建项目目录
mkdir C:\CTF-Platform
cd C:\CTF-Platform

# 克隆项目（如果有Git仓库）
git clone https://github.com/rookiebeimo/create-ctf_work.git
```



**方式二：手动下载**

1. 将项目文件复制到 `C:\CTF-Platform`

2. 确保目录结构如下：

   ```
   C:\CTF-Platform\
   ├── app.py
   ├── models.py
   ├── config.py
   ├── requirements.txt
   ├── init_database.py
   ├── utils\
   ├── routes\
   └── storage\
   ```

   

### 2. 创建虚拟环境

```
cd C:\CTF-Platform

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 激活后提示符会显示 (venv)
```



**注意**：每次打开新的命令窗口运行项目时，都需要激活虚拟环境。

### 3. 安装Python依赖

```
# 确保在虚拟环境中
venv\Scripts\activate

# 安装依赖包
pip install -r requirements.txt

# 如果MySQL驱动安装失败，单独安装：
pip install mysqlclient
# 或者
pip install pymysql
```



### 4. 修改配置文件

编辑 `config.py`，根据你的环境修改配置：

```
# 主要修改以下配置：

# MySQL配置（根据实际修改）
MYSQL_HOST = 'localhost'          # 本地MySQL
MYSQL_PORT = 3306                # MySQL端口
MYSQL_USER = 'ctf_user'          # 数据库用户
MYSQL_PASSWORD = '031006'        # 数据库密码
MYSQL_DATABASE = 'ctf_platform'  # 数据库名

# 应用密钥（生产环境必须修改）
SECRET_KEY = 'your-secret-key-here'  # 生成随机字符串

# 文件上传路径（确保目录存在）
UPLOAD_FOLDER = 'C:\\CTF-Platform\\storage'

# 如果是生产环境，设置环境变量
# set FLASK_ENV=production
```



### 5. 初始化数据库

```
# 确保在项目目录下且虚拟环境已激活
cd C:\CTF-Platform
venv\Scripts\activate

# 方法一：使用Flask命令（推荐）
flask init-db

# 方法二：直接运行初始化脚本
python init_database.py
```



输出应显示：

```
正在初始化CTF平台数据库...
数据库初始化完成！
创建的表: users, categories, challenges, submissions, system_logs
默认分类: ['Web', 'Pwn', 'Reverse', 'Crypto', 'Misc', 'Forensics']
管理员用户: ['admin']
```



### 6. 创建管理员账户

```
# 如果init-db命令未创建管理员，手动创建
flask create-admin

# 根据提示输入：
# 用户名: admin
# 邮箱: admin@yourdomain.com
# 密码: your-strong-password
```



### 7. 测试运行

#### 开发模式运行：

```
# 设置开发环境
set FLASK_ENV=development
set FLASK_APP=app.py

# 运行开发服务器
flask run --host=0.0.0.0 --port=5000
```



#### 生产模式运行：

```
# 设置生产环境
set FLASK_ENV=production
set FLASK_APP=app.py

# 运行生产服务器（使用waitress作为WSGI服务器）
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 app:app
```



### 8. 验证部署

1. **后端验证**：

   - 访问 `http://localhost:5000/health`
   - 应返回JSON健康状态信息
   - 访问 `http://localhost:5000/` 查看API信息

2. **前端验证**：

   - 打开浏览器访问 `http://localhost:5000`（如果前端整合）
   - 或访问前端HTML文件路径

3. **API测试**：

   ```
   # 使用curl测试API
   curl http://localhost:5000/
   curl http://localhost:5000/health
   ```

   

## 🚀 生产环境部署优化

### 1. 使用Windows服务运行

创建服务文件 `ctf-platform-service.xml`（用于NSSM工具）：

```
<service>
  <id>CTFPlatform</id>
  <name>CTF Platform Service</name>
  <description>CTF平台Web服务</description>
  <executable>C:\CTF-Platform\venv\Scripts\python.exe</executable>
  <arguments>C:\CTF-Platform\app.py</arguments>
  <log mode="roll"></log>
  <workingdirectory>C:\CTF-Platform</workingdirectory>
  <env name="FLASK_ENV" value="production" />
  <env name="PYTHONPATH" value="C:\CTF-Platform" />
</service>
```



使用NSSM安装服务：

```
# 下载NSSM：https://nssm.cc/download
nssm install CTFPlatform c:\CTF-Platform\venv\Scripts\python.exe c:\CTF-Platform\app.py
nssm set CTFPlatform AppEnvironmentExtra FLASK_ENV=production
net start CTFPlatform
```



### 2. 使用IIS部署（可选）

1. 安装IIS和URL Rewrite模块

2. 安装wfastcgi：

   ```
   pip install wfastcgi
   wfastcgi-enable
   ```

   

3. 在IIS中创建网站，指向项目目录

4. 配置web.config文件

### 3. 配置反向代理（如果需要）

使用Nginx或Apache作为反向代理：

```
# Nginx配置示例
location / {
    proxy_pass http://127.0.0.1:5000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```



## 🔒 安全配置

### 1. 修改默认密码

- MySQL root密码
- 管理员账户密码
- 应用SECRET_KEY

### 2. 防火墙配置

```
# 开放端口（如果需要外部访问）
netsh advfirewall firewall add rule name="CTF Platform HTTP" dir=in action=allow protocol=TCP localport=5000

# 或者限制访问IP
netsh advfirewall firewall add rule name="CTF Platform HTTP" dir=in action=allow protocol=TCP localport=5000 remoteip=192.168.1.0/24
```



### 3. 文件权限设置

```
# 设置storage目录权限
icacls C:\CTF-Platform\storage /grant "IIS_IUSRS:(OI)(CI)F"
icacls C:\CTF-Platform\storage /grant "NETWORK SERVICE:(OI)(CI)F"
```



## 📊 日常运维

### 1. 启动/停止服务

```
# 手动启动
cd C:\CTF-Platform
venv\Scripts\activate
set FLASK_ENV=production
python app.py

# 或使用服务
net start CTFPlatform
net stop CTFPlatform
```



### 2. 查看日志

```
# 应用日志
type C:\CTF-Platform\storage\logs\ctf_platform.log

# 错误日志查看
findstr /i "ERROR" C:\CTF-Platform\storage\logs\ctf_platform.log

# 实时日志监控（需要PowerShell）
Get-Content C:\CTF-Platform\storage\logs\ctf_platform.log -Wait
```



### 3. 备份与恢复

**数据库备份**：

```
# 备份数据库
mysqldump -u ctf_user -p031006 ctf_platform > backup_%date:~0,4%%date:~5,2%%date:~8,2%.sql

# 恢复数据库
mysql -u ctf_user -p031006 ctf_platform < backup.sql
```



**应用数据备份**：

```
# 备份uploads和配置
xcopy C:\CTF-Platform\storage C:\Backup\CTF-Platform\storage /E /I /Y
xcopy C:\CTF-Platform\*.py C:\Backup\CTF-Platform\ /Y
```



### 4. 更新代码

```
cd C:\CTF-Platform

# 暂停服务
net stop CTFPlatform

# 备份当前版本
xcopy . C:\Backup\CTF-Platform_%date:~0,4%%date:~5,2%%date:~8,2% /E /I

# 更新代码（如果使用Git）
git pull

# 更新依赖
venv\Scripts\activate
pip install -r requirements.txt --upgrade

# 数据库迁移（如果有）
flask db upgrade

# 重启服务
net start CTFPlatform
```



## 🐛 故障排除

### 常见问题

1. **端口占用**：

   ```
   # 查看占用5000端口的进程
   netstat -ano | findstr :5000
   
   # 杀死进程（PID从上面命令获取）
   taskkill /PID <PID> /F
   ```

   

2. **MySQL连接失败**：

   - 检查MySQL服务是否运行：`net start mysql`
   - 检查用户权限：`mysql -u ctf_user -p`
   - 检查防火墙：`netsh advfirewall firewall show rule name=all`

3. **Python包安装失败**：

   ```
   # 更新pip
   python -m pip install --upgrade pip
   
   # 使用国内镜像
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
   ```

   

4. **内存不足**：

   - 增加虚拟内存
   - 优化MySQL配置
   - 减少并发连接数

### 调试模式

```
# 启用调试模式
set FLASK_ENV=development
set FLASK_DEBUG=1
python app.py
```



## 📞 支持与帮助

### 获取帮助

1. 查看项目README文件
2. 查看Flask日志文件
3. 检查Windows事件查看器
4. 在GitHub Issues中提问

### 应急联系人

- 系统管理员：林哲凯
- 开发支持：卢圣轩
- 数据库管理员：林文进

------

**部署完成提示**：当看到以下信息时，表示部署成功：

- 访问 `http://localhost:5000/health` 返回健康状态
- MySQL数据库中有ctf_platform库和相关表
- 管理员账户可以正常登录
- 题目列表可以正常加载