

# CTF平台 - CI/CD流水线说明

## 📖 概述

本文档描述CTF平台的持续集成/持续部署（CI/CD）流程。虽然这是一个Windows部署的项目，我们仍然可以通过自动化工具来简化部署和维护流程。

## 🛠️ 自动化部署策略

### 总体流程

- # CTF平台 - CI/CD流水线说明


  ## 📖 概述


  本文档描述CTF平台的持续集成/持续部署（CI/CD）流程。虽然这是一个Windows部署的项目，我们仍然可以通过自动化工具来简化部署和维护流程。


  ## 🛠️ 自动化部署策略


  ### 总体流程

## 🔄 手动部署流程（无Docker）

### 部署脚本示例

创建部署脚本 `deploy.bat`：

```
@echo off
echo ============================================
echo CTF平台部署脚本
echo 开始时间: %date% %time%
echo ============================================

REM 1. 停止现有服务
echo [1/7] 停止现有服务...
net stop CTFPlatform 2>nul || echo 服务未运行或不存在

REM 2. 备份当前版本
echo [2/7] 备份当前版本...
set BACKUP_DIR=C:\Backups\CTF-Platform_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%
mkdir "%BACKUP_DIR%" 2>nul
xcopy "C:\CTF-Platform\*.*" "%BACKUP_DIR%\" /E /I /Y >nul
echo 备份完成: %BACKUP_DIR%

REM 3. 清理旧文件
echo [3/7] 清理旧文件...
cd /d "C:\CTF-Platform"
rd /s /q "venv" 2>nul
del /q *.pyc 2>nul
del /q *.log 2>nul

REM 4. 更新代码（从Git）
echo [4/7] 更新代码...
if exist ".git" (
    git pull origin main
    if errorlevel 1 (
        echo Git拉取失败，使用备份恢复
        xcopy "%BACKUP_DIR%\*.*" "." /E /I /Y
    )
) else (
    echo 未发现Git仓库，手动更新代码
    pause
)

REM 5. 设置Python环境
echo [5/7] 设置Python环境...
python -m venv venv
call venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

REM 6. 数据库迁移
echo [6/7] 数据库迁移...
flask db upgrade 2>nul || echo 无需数据库迁移
flask update-scores

REM 7. 启动服务
echo [7/7] 启动服务...
net start CTFPlatform
if errorlevel 1 (
    echo 服务启动失败，检查配置
    pause
    exit /b 1
)

REM 健康检查
echo 等待服务启动...
timeout /t 10 /nobreak >nul

echo 进行健康检查...
curl -f http://localhost:5000/health >nul 2>&1
if errorlevel 1 (
    echo 健康检查失败！
    pause
    exit /b 1
)

echo ============================================
echo 部署成功完成！
echo 结束时间: %date% %time%
echo 访问地址: http://localhost:5000
echo ============================================
pause
```

## 🔧 GitHub Actions自动化（如果使用GitHub）

创建 `.github/workflows/deploy.yml`：

```
name: Deploy CTF Platform to Windows Server

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Lint with flake8
      run: |
        pip install flake8
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    
    - name: Run unit tests
      run: |
        python -m pytest tests/ -v

  deploy:
    needs: test
    runs-on: windows-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy to Windows Server via SSH
      uses: appleboy/ssh-action@v0.1.4
      with:
        host: ${{ secrets.DEPLOY_HOST }}
        username: ${{ secrets.DEPLOY_USER }}
        password: ${{ secrets.DEPLOY_PASSWORD }}
        script: |
          cd /c/CTF-Platform
          git pull origin main
          call venv/Scripts/activate
          pip install -r requirements.txt --upgrade
          flask db upgrade
          net stop CTFPlatform
          net start CTFPlatform
          timeout /t 10
          curl -f http://localhost:5000/health || exit 1
```



## 🧪 Jenkins流水线配置（如果使用Jenkins）

创建 `Jenkinsfile`：

```
pipeline {
    agent {
        label 'windows'
    }
    
    environment {
        PROJECT_PATH = 'C:\\CTF-Platform'
        VENV_PATH = 'C:\\CTF-Platform\\venv'
        DEPLOY_LOG = 'C:\\Logs\\ctf-deploy.log'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                bat 'echo 开始部署CTF平台 > "%DEPLOY_LOG%"'
            }
        }
        
        stage('Install Dependencies') {
            steps {
                bat '''
                    cd "%PROJECT_PATH%"
                    if not exist "%VENV_PATH%" (
                        python -m venv venv
                    )
                    call "%VENV_PATH%\\Scripts\\activate"
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                bat '''
                    cd "%PROJECT_PATH%"
                    call "%VENV_PATH%\\Scripts\\activate"
                    python -m pytest tests/ -v
                '''
            }
        }
        
        stage('Database Migration') {
            steps {
                bat '''
                    cd "%PROJECT_PATH%"
                    call "%VENV_PATH%\\Scripts\\activate"
                    flask db upgrade 2>nul || echo 无需迁移
                    flask update-scores
                '''
            }
        }
        
        stage('Deploy') {
            steps {
                bat '''
                    net stop CTFPlatform 2>nul || echo 服务未运行
                    timeout /t 5
                    
                    cd "%PROJECT_PATH%"
                    call "%VENV_PATH%\\Scripts\\activate"
                    set FLASK_ENV=production
                    
                    rem 使用waitress启动（生产环境）
                    start /B waitress-serve --host=0.0.0.0 --port=5000 app:app
                    
                    rem 或者注册为服务
                    rem nssm start CTFPlatform
                    
                    echo 等待服务启动...
                    timeout /t 10
                    
                    rem 健康检查
                    curl http://localhost:5000/health
                    if %errorlevel% neq 0 (
                        echo 部署失败！ >> "%DEPLOY_LOG%"
                        exit 1
                    )
                    
                    echo 部署成功！ >> "%DEPLOY_LOG%"
                '''
            }
        }
        
        stage('Verify Deployment') {
            steps {
                bat '''
                    echo 验证部署...
                    curl -f http://localhost:5000/health
                    curl -f http://localhost:5000/api/v1/challenges
                    echo 验证完成！
                '''
            }
        }
    }
    
    post {
        success {
            emailext (
                subject: "CTF平台部署成功 - ${env.JOB_NAME}",
                body: "构建 ${env.BUILD_NUMBER} 部署成功\n\n访问地址：http://your-server:5000",
                to: 'team@example.com'
            )
        }
        failure {
            emailext (
                subject: "CTF平台部署失败 - ${env.JOB_NAME}",
                body: "构建 ${env.BUILD_NUMBER} 部署失败\n\n请查看日志：${env.BUILD_URL}",
                to: 'devops@example.com'
            )
        }
    }
}
```



## 📊 部署检查清单

### 预部署检查

- 数据库备份完成
- 配置文件已更新
- 依赖包版本已锁定
- 测试环境验证通过
- 部署计划已通知相关人员

### 部署中检查

- 服务正常停止
- 代码更新完成
- 数据库迁移完成
- 服务正常启动
- 健康检查通过

### 部署后验证

- 首页可以访问
- 用户登录正常
- 题目加载正常
- 提交功能正常
- 排行榜正常显示

## 🚨 回滚流程

### 自动回滚脚本 `rollback.bat`：

```
@echo off
echo ============================================
echo CTF平台回滚脚本
echo ============================================

REM 获取最新的备份
for /f "delims=" %%i in ('dir C:\Backups /b /ad /od') do set LAST_BACKUP=%%i

if "%LAST_BACKUP%"=="" (
    echo 未找到备份文件！
    pause
    exit /b 1
)

echo 准备回滚到备份: %LAST_BACKUP%
set BACKUP_PATH=C:\Backups\%LAST_BACKUP%

REM 停止服务
echo 停止服务...
net stop CTFPlatform 2>nul || echo 服务未运行

REM 回滚文件
echo 回滚文件...
cd /d "C:\CTF-Platform"
rd /s /q "venv" 2>nul
xcopy "%BACKUP_PATH%\*.*" "." /E /I /Y /Q

REM 恢复数据库
echo 恢复数据库...
set DB_BACKUP=%BACKUP_PATH%\database_backup.sql
if exist "%DB_BACKUP%" (
    mysql -u ctf_user -p031006 ctf_platform < "%DB_BACKUP%"
)

REM 启动服务
echo 启动服务...
net start CTFPlatform

echo 回滚完成！
echo 当前版本: %LAST_BACKUP%
pause
```



## 📈 部署监控

### 监控脚本 `monitor-deployment.ps1`：

```
# CTF平台部署监控脚本
$ServiceName = "CTFPlatform"
$HealthUrl = "http://localhost:5000/health"
$LogFile = "C:\Logs\deployment-monitor.log"

function Write-Log {
    param([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$Timestamp - $Message" | Out-File -FilePath $LogFile -Append
    Write-Host $Message
}

Write-Log "开始监控CTF平台部署状态..."

# 检查服务状态
$Service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($Service.Status -ne "Running") {
    Write-Log "错误：服务 $ServiceName 未运行"
    exit 1
}

# 健康检查
try {
    $Response = Invoke-RestMethod -Uri $HealthUrl -Method Get -TimeoutSec 10
    if ($Response.status -eq "healthy") {
        Write-Log "健康检查通过"
    } else {
        Write-Log "警告：健康检查返回状态：$($Response.status)"
    }
} catch {
    Write-Log "错误：健康检查失败 - $($_.Exception.Message)"
    exit 1
}

# 检查关键端点
$Endpoints = @(
    "http://localhost:5000/api/v1/challenges",
    "http://localhost:5000/api/v1/leaderboard",
    "http://localhost:5000/api/v1/auth/login"
)

foreach ($Endpoint in $Endpoints) {
    try {
        $Status = (Invoke-WebRequest -Uri $Endpoint -Method Head -TimeoutSec 5).StatusCode
        Write-Log "$Endpoint - HTTP $Status"
    } catch {
        Write-Log "警告：$Endpoint 不可用 - $($_.Exception.Message)"
    }
}

Write-Log "监控完成"
```



## 🔍 部署问题诊断

### 常见问题诊断表

| 问题           | 可能原因             | 解决方案                         |
| :------------- | :------------------- | :------------------------------- |
| 服务无法启动   | 端口被占用           | 使用 `netstat -ano` 查看端口占用 |
| MySQL连接失败  | 密码错误或服务未启动 | 检查MySQL服务状态和凭据          |
| 导入依赖失败   | 网络问题或包冲突     | 使用国内镜像源，清理pip缓存      |
| 数据库迁移失败 | 数据库权限不足       | 检查数据库用户权限               |
| 静态文件404    | 文件路径错误         | 检查UPLOAD_FOLDER配置            |
| 性能缓慢       | 内存不足或配置不当   | 优化MySQL配置，增加内存          |

### 诊断命令集

```
# 诊断脚本
.\diagnose.ps1

# 手动诊断命令
Get-Service CTFPlatform
netstat -ano | Select-String ":5000"
Test-NetConnection localhost -Port 5000
Get-Content C:\CTF-Platform\storage\logs\ctf_platform.log -Tail 100
```



## 📋 版本发布流程

### 版本号规范

- 主版本.次版本.修订版本 (如：v1.2.3)
- 主版本：重大功能更新
- 次版本：新功能添加
- 修订版本：Bug修复

### 发布流程

1. **准备阶段**
   - 更新CHANGELOG.md
   - 更新版本号
   - 创建发布分支
2. **测试阶段**
   - 运行完整测试套件
   - 手动测试关键功能
   - 性能测试
3. **发布阶段**
   - 合并到主分支
   - 打标签：`git tag v1.2.3`
   - 推送到远程：`git push origin v1.2.3`
4. **部署阶段**
   - 执行部署脚本
   - 验证部署
   - 发送发布通知

## 🔐 安全部署实践

### 安全清单

- 使用HTTPS（生产环境）
- 数据库连接使用SSL
- 敏感信息使用环境变量
- 定期更新依赖包
- 启用防火墙规则
- 配置访问日志
- 定期备份数据

### 安全扫描

```
# 使用safety检查依赖安全
pip install safety
safety check -r requirements.txt

# 使用bandit扫描代码安全
pip install bandit
bandit -r .
```

