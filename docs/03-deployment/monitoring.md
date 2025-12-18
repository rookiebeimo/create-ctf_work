### 监控和日志指南

# CTF平台 - 监控和日志指南

## 📊 监控概览

CTF平台的监控系统分为三个层次：

1. **基础设施监控**：服务器资源使用情况
2. **应用监控**：应用性能和健康状态
3. **业务监控**：用户活动和平台使用情况

## 🔧 监控工具选择（Windows环境）

### 推荐监控方案

- **资源监控**：Windows性能监视器 + 自定义脚本
- **日志管理**：Filebeat + ELK Stack 或 纯文件日志
- **应用监控**：自定义健康检查 + 告警系统
- **数据库监控**：MySQL性能监控 + 慢查询日志

## 📈 系统资源监控

### 1. Windows性能监视器设置

创建数据收集器集：

```powershell
# 创建监控数据收集器
$DataCollectorSet = New-Object -COM Pla.DataCollectorSet
$DataCollectorSet.DisplayName = "CTF平台性能监控"
$DataCollectorSet.Duration = 86400  # 24小时

# 添加性能计数器
$DataCollector = $DataCollectorSet.DataCollectors.CreateDataCollector(0)
$DataCollector.FileName = "C:\PerfLogs\CTF-Platform\perf.csv"
$DataCollector.LogFileFormat = 3  # CSV格式

# 关键性能计数器
$Counters = @(
    "\Processor(_Total)\% Processor Time",
    "\Memory\Available MBytes",
    "\Process(python)\% Processor Time",
    "\Process(python)\Working Set",
    "\LogicalDisk(C:)\% Free Space",
    "\Network Interface(*)\Bytes Total/sec",
    "\TCPv4\Connections Established"
)

$DataCollector.PerformanceCounters = $Counters
$DataCollectorSet.DataCollectors.Add($DataCollector)
$DataCollectorSet.Commit("CTF平台性能监控", $null, 0x0003)
$DataCollectorSet.Start($false)
```

### 2. 自定义监控脚本

创建 `monitor-system.ps1`：

```
# CTF平台系统监控脚本
$LogDir = "C:\CTF-Platform\storage\logs\monitoring"
$LogFile = "$LogDir\system-monitor-$(Get-Date -Format 'yyyyMMdd').log"
$Thresholds = @{
    "CPU" = 80
    "Memory" = 85
    "Disk" = 90
    "Connections" = 1000
}

# 确保日志目录存在
if (!(Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force
}

function Write-MonitorLog {
    param([string]$Level, [string]$Message, [string]$Metric, [int]$Value)
    
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "$Timestamp [$Level] $Message | $Metric=$Value"
    
    Add-Content -Path $LogFile -Value $LogEntry
    
    # 如果超过阈值，发送告警
    if ($Level -eq "WARNING" -or $Level -eq "ERROR") {
        Send-Alert -Level $Level -Message $Message -Metric $Metric -Value $Value
    }
}

function Get-SystemMetrics {
    $CPU = (Get-Counter "\Processor(_Total)\% Processor Time").CounterSamples.CookedValue
    $Memory = (Get-Counter "\Memory\% Committed Bytes In Use").CounterSamples.CookedValue
    $Disk = (Get-Counter "\LogicalDisk(C:)\% Free Space").CounterSamples.CookedValue
    $Connections = (Get-NetTCPConnection -State Established).Count
    
    # 检查Python进程
    $PythonProcess = Get-Process python -ErrorAction SilentlyContinue
    $PythonMemory = if ($PythonProcess) { $PythonProcess.WorkingSet64 / 1MB } else { 0 }
    
    return @{
        "CPU" = [math]::Round($CPU, 2)
        "Memory" = [math]::Round($Memory, 2)
        "DiskFree" = [math]::Round($Disk, 2)
        "Connections" = $Connections
        "PythonMemoryMB" = [math]::Round($PythonMemory, 2)
    }
}

function Check-Thresholds {
    param($Metrics)
    
    foreach ($Key in $Metrics.Keys) {
        $Value = $Metrics[$Key]
        
        switch ($Key) {
            "CPU" {
                if ($Value -gt $Thresholds.CPU) {
                    Write-MonitorLog "WARNING" "CPU使用率过高" $Key $Value
                }
            }
            "Memory" {
                if ($Value -gt $Thresholds.Memory) {
                    Write-MonitorLog "WARNING" "内存使用率过高" $Key $Value
                }
            }
            "DiskFree" {
                if ($Value -lt (100 - $Thresholds.Disk)) {
                    Write-MonitorLog "WARNING" "磁盘空间不足" $Key $Value
                }
            }
            "Connections" {
                if ($Value -gt $Thresholds.Connections) {
                    Write-MonitorLog "WARNING" "TCP连接数过多" $Key $Value
                }
            }
        }
    }
}

# 主监控循环
while ($true) {
    $Metrics = Get-SystemMetrics
    Check-Thresholds -Metrics $Metrics
    
    # 正常日志
    $LogMessage = "系统状态正常 - " + 
                  "CPU: $($Metrics.CPU)%, " +
                  "内存: $($Metrics.Memory)%, " +
                  "磁盘: $($Metrics.DiskFree)%可用, " +
                  "连接: $($Metrics.Connections), " +
                  "Python内存: $($Metrics.PythonMemoryMB)MB"
    
    Write-MonitorLog "INFO" $LogMessage "System" 0
    
    # 每分钟检查一次
    Start-Sleep -Seconds 60
}
```



## 📝 应用日志监控

### 1. 应用日志配置

Flask应用已配置日志系统（见`log.py`），日志文件位于：

- 主日志：`C:\CTF-Platform\storage\logs\ctf_platform.log`
- 访问日志：通过RequestLogger中间件记录

### 2. 日志分析脚本

创建 `analyze-logs.ps1`：

```
# CTF平台日志分析脚本
$LogFile = "C:\CTF-Platform\storage\logs\ctf_platform.log"
$ReportFile = "C:\CTF-Platform\storage\logs\daily-report-$(Get-Date -Format 'yyyyMMdd').txt"

function Generate-DailyReport {
    # 获取当天日志
    $Today = Get-Date -Format "yyyy-MM-dd"
    $TodayLogs = Select-String -Path $LogFile -Pattern $Today
    
    $Report = @"
CTF平台每日报告
日期: $Today
生成时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

============================================
1. 请求统计
============================================
"@
    
    # 统计请求
    $Requests = $TodayLogs | Where-Object { $_ -match "REQUEST" }
    $TotalRequests = $Requests.Count
    $SuccessfulRequests = ($Requests | Where-Object { $_ -match "Status:2\d\d" }).Count
    $ErrorRequests = ($Requests | Where-Object { $_ -match "Status:(4|5)\d\d" }).Count
    
    $Report += "总请求数: $TotalRequests`n"
    $Report += "成功请求: $SuccessfulRequests`n"
    $Report += "错误请求: $ErrorRequests`n"
    $Report += "成功率: " + ([math]::Round(($SuccessfulRequests / $TotalRequests * 100), 2)) + "%`n"
    
    $Report += @"

============================================
2. 安全事件统计
============================================
"@
    
    $SecurityEvents = $TodayLogs | Where-Object { $_ -match "SECURITY" }
    $Report += "安全事件总数: $($SecurityEvents.Count)`n"
    
    # 按类型统计
    $EventTypes = @{
        "LOGIN" = 0
        "SUBMISSION" = 0
        "ADMIN" = 0
        "ERROR" = 0
    }
    
    foreach ($Event in $SecurityEvents) {
        if ($Event -match "LOGIN") { $EventTypes.LOGIN++ }
        elseif ($Event -match "SUBMISSION") { $EventTypes.SUBMISSION++ }
        elseif ($Event -match "ADMIN") { $EventTypes.ADMIN++ }
        elseif ($Event -match "ERROR") { $EventTypes.ERROR++ }
    }
    
    foreach ($Key in $EventTypes.Keys) {
        $Report += "$Key 事件: $($EventTypes[$Key])`n"
    }
    
    $Report += @"

============================================
3. 用户活跃度
============================================
"@
    
    # 提取用户活动
    $UserLogins = $TodayLogs | Where-Object { $_ -match "User logged in" }
    $UniqueUsers = ($UserLogins | ForEach-Object { 
        if ($_ -match "User:(\d+)") { $matches[1] }
    } | Sort-Object -Unique).Count
    
    $Report += "活跃用户数: $UniqueUsers`n"
    
    $Report += @"

============================================
4. 错误统计
============================================
"@
    
    $Errors = $TodayLogs | Where-Object { $_ -match "ERROR|CRITICAL" }
    $Report += "错误总数: $($Errors.Count)`n"
    
    # 错误类型分布
    $ErrorPatterns = @(
        "数据库连接",
        "文件上传",
        "认证失败",
        "API错误",
        "其他"
    )
    
    $ErrorCounts = @{}
    foreach ($Pattern in $ErrorPatterns) {
        $ErrorCounts[$Pattern] = ($Errors | Where-Object { $_ -match $Pattern }).Count
    }
    
    foreach ($Key in $ErrorCounts.Keys) {
        if ($ErrorCounts[$Key] -gt 0) {
            $Report += "$Key 错误: $($ErrorCounts[$Key])`n"
        }
    }
    
    $Report += @"

============================================
5. 性能指标
============================================
"@
    
    # 提取响应时间
    $ResponseTimes = @()
    foreach ($Request in $Requests) {
        if ($Request -match "Time:([\d\.]+)ms") {
            $ResponseTimes += [double]$matches[1]
        }
    }
    
    if ($ResponseTimes.Count -gt 0) {
        $AvgResponseTime = [math]::Round(($ResponseTimes | Measure-Object -Average).Average, 2)
        $MaxResponseTime = [math]::Round(($ResponseTimes | Measure-Object -Maximum).Maximum, 2)
        $MinResponseTime = [math]::Round(($ResponseTimes | Measure-Object -Minimum).Minimum, 2)
        
        $Report += "平均响应时间: ${AvgResponseTime}ms`n"
        $Report += "最大响应时间: ${MaxResponseTime}ms`n"
        $Report += "最小响应时间: ${MinResponseTime}ms`n"
    }
    
    # 保存报告
    $Report | Out-File -FilePath $ReportFile -Encoding UTF8
    
    # 发送报告邮件（可选）
    if ($SendEmail) {
        Send-ReportEmail -ReportFile $ReportFile
    }
    
    Write-Host "日报已生成: $ReportFile"
}

# 定时生成报告（每天凌晨1点）
while ($true) {
    $CurrentHour = (Get-Date).Hour
    if ($CurrentHour -eq 1) {
        Generate-DailyReport
        # 等待23小时后再检查
        Start-Sleep -Seconds (23 * 3600)
    } else {
        # 每小时检查一次
        Start-Sleep -Seconds 3600
    }
}
```



### 3. 实时日志监控

创建 `tail-logs.ps1`：

```
# 实时日志监控工具
param(
    [string]$LogPath = "C:\CTF-Platform\storage\logs\ctf_platform.log",
    [switch]$Follow,
    [int]$Lines = 50,
    [string]$Filter
)

# 显示指定行数
if ($Lines -gt 0) {
    Get-Content -Path $LogPath -Tail $Lines | ForEach-Object {
        if ($Filter) {
            if ($_ -match $Filter) { $_ }
        } else {
            $_
        }
    }
}

# 实时跟踪
if ($Follow) {
    Write-Host "开始实时监控日志 (Ctrl+C 退出)" -ForegroundColor Green
    Get-Content -Path $LogPath -Wait -Tail 10 | ForEach-Object {
        # 根据日志级别着色
        switch -Regex ($_) {
            "ERROR|CRITICAL" { Write-Host $_ -ForegroundColor Red }
            "WARNING" { Write-Host $_ -ForegroundColor Yellow }
            "INFO" { Write-Host $_ -ForegroundColor Green }
            "DEBUG" { Write-Host $_ -ForegroundColor Gray }
            default { Write-Host $_ }
        }
    }
}
```



## 🗄️ 数据库监控

### 1. MySQL性能监控

创建 `monitor-mysql.ps1`：

```
# MySQL数据库监控脚本
$MySQLUser = "ctf_user"
$MySQLPassword = "031006"
$MySQLDatabase = "ctf_platform"
$LogFile = "C:\CTF-Platform\storage\logs\mysql-monitor-$(Get-Date -Format 'yyyyMMdd').log"

function Get-MySQLMetrics {
    # 连接MySQL获取性能指标
    $Connection = New-Object MySql.Data.MySqlClient.MySqlConnection
    $Connection.ConnectionString = "server=localhost;user=$MySQLUser;password=$MySQLPassword;database=$MySQLDatabase;"
    
    try {
        $Connection.Open()
        
        $Queries = @{
            "连接数" = "SHOW STATUS LIKE 'Threads_connected'"
            "运行线程" = "SHOW STATUS LIKE 'Threads_running'"
            "查询缓存" = "SHOW STATUS LIKE 'Qcache_hits'"
            "慢查询" = "SHOW STATUS LIKE 'Slow_queries'"
            "表锁" = "SHOW STATUS LIKE 'Table_locks_waited'"
            "内存使用" = "SELECT @@innodb_buffer_pool_size/1024/1024 as buffer_pool_mb"
        }
        
        $Metrics = @{}
        
        foreach ($Key in $Queries.Keys) {
            $Command = $Connection.CreateCommand()
            $Command.CommandText = $Queries[$Key]
            $Reader = $Command.ExecuteReader()
            
            if ($Reader.Read()) {
                if ($Key -eq "内存使用") {
                    $Metrics[$Key] = [math]::Round($Reader.GetValue(0), 2)
                } else {
                    $Metrics[$Key] = $Reader.GetValue(1)
                }
            }
            
            $Reader.Close()
        }
        
        return $Metrics
    } catch {
        Write-Error "MySQL监控失败: $_"
        return $null
    } finally {
        if ($Connection.State -eq "Open") {
            $Connection.Close()
        }
    }
}

# 监控循环
while ($true) {
    $Metrics = Get-MySQLMetrics
    
    if ($Metrics) {
        $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        $LogEntry = "$Timestamp [MySQL] " + 
                    "连接: $($Metrics['连接数']), " +
                    "运行线程: $($Metrics['运行线程']), " +
                    "查询缓存命中: $($Metrics['查询缓存']), " +
                    "慢查询: $($Metrics['慢查询']), " +
                    "表锁等待: $($Metrics['表锁']), " +
                    "缓冲池: $($Metrics['内存使用'])MB"
        
        Add-Content -Path $LogFile -Value $LogEntry
        
        # 检查阈值
        if ([int]$Metrics['连接数'] -gt 100) {
            Write-Warning "MySQL连接数过高: $($Metrics['连接数'])"
        }
        
        if ([int]$Metrics['慢查询'] -gt 10) {
            Write-Warning "慢查询数量较多: $($Metrics['慢查询'])"
        }
    }
    
    Start-Sleep -Seconds 300  # 每5分钟检查一次
}
```



### 2. 慢查询日志配置

修改MySQL配置文件 `my.ini`：

```
[mysqld]
# 启用慢查询日志
slow_query_log = 1
slow_query_log_file = "C:/ProgramData/MySQL/MySQL Server 8.0/Data/slow.log"
long_query_time = 2
log_queries_not_using_indexes = 1
```



## 🚨 告警系统

### 1. 邮件告警配置

创建 `alert-system.ps1`：

```
# 告警系统
param(
    [string]$SmtpServer = "smtp.gmail.com",
    [int]$SmtpPort = 587,
    [string]$FromEmail = "alerts@ctfplatform.com",
    [string]$ToEmail = "admin@yourdomain.com",
    [string]$SmtpUser,
    [string]$SmtpPassword
)

function Send-Alert {
    param(
        [string]$Level,
        [string]$Subject,
        [string]$Message,
        [string]$Metric,
        [string]$Value
    )
    
    $Body = @"
CTF平台告警通知

级别: $Level
时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
指标: $Metric
当前值: $Value

详细描述:
$Message

请及时处理。

-- 
CTF平台监控系统
"@
    
    # 发送邮件
    $MailParams = @{
        From = $FromEmail
        To = $ToEmail
        Subject = "[CTF平台] $Subject"
        Body = $Body
        SmtpServer = $SmtpServer
        Port = $SmtpPort
    }
    
    if ($SmtpUser -and $SmtpPassword) {
        $MailParams.Credential = New-Object System.Management.Automation.PSCredential($SmtpUser, (ConvertTo-SecureString $SmtpPassword -AsPlainText -Force))
        $MailParams.UseSsl = $true
    }
    
    Send-MailMessage @MailParams
    
    # 记录告警
    $AlertLog = "C:\CTF-Platform\storage\logs\alerts-$(Get-Date -Format 'yyyyMMdd').log"
    $LogEntry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') [$Level] $Subject | $Metric=$Value"
    Add-Content -Path $AlertLog -Value $LogEntry
}

# 告警规则
$AlertRules = @{
    "high_cpu" = @{
        Check = { param($m) $m.CPU -gt 90 }
        Message = "CPU使用率超过90%"
        Level = "CRITICAL"
    }
    "high_memory" = @{
        Check = { param($m) $m.Memory -gt 95 }
        Message = "内存使用率超过95%"
        Level = "CRITICAL"
    }
    "low_disk" = @{
        Check = { param($m) $m.DiskFree -lt 10 }
        Message = "磁盘剩余空间不足10%"
        Level = "WARNING"
    }
    "mysql_slow" = @{
        Check = { param($m) $m.SlowQueries -gt 20 }
        Message = "MySQL慢查询超过20个"
        Level = "WARNING"
    }
}

# 检查并触发告警
function Check-Alerts {
    param($SystemMetrics, $MySqlMetrics)
    
    $AllMetrics = @{}
    if ($SystemMetrics) { $AllMetrics += $SystemMetrics }
    if ($MySqlMetrics) { 
        $AllMetrics += @{
            "SlowQueries" = $MySqlMetrics["慢查询"]
        }
    }
    
    foreach ($RuleName in $AlertRules.Keys) {
        $Rule = $AlertRules[$RuleName]
        
        if ($Rule.Check.Invoke($AllMetrics)) {
            Send-Alert -Level $Rule.Level `
                       -Subject $Rule.Message `
                       -Message $Rule.Message `
                       -Metric $RuleName `
                       -Value $AllMetrics[$RuleName]
        }
    }
}
```



### 2. 短信/钉钉告警（可选）

```
# 钉钉机器人告警
function Send-DingTalkAlert {
    param(
        [string]$WebhookUrl,
        [string]$Message,
        [string]$Level = "WARNING"
    )
    
    $Color = switch ($Level) {
        "CRITICAL" { "FF0000" }
        "WARNING" { "FF9900" }
        default { "00CC00" }
    }
    
    $Body = @{
        msgtype = "markdown"
        markdown = @{
            title = "CTF平台告警"
            text = "### CTF平台告警通知`n" +
                   "**级别**: $Level`n" +
                   "**时间**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n" +
                   "**内容**: $Message`n" +
                   "**服务器**: $(hostname)"
        }
        at = @{
            isAtAll = $false
        }
    } | ConvertTo-Json
    
    Invoke-RestMethod -Uri $WebhookUrl -Method Post -Body $Body -ContentType "application/json"
}
```



## 📊 Grafana监控仪表板（可选）

### 1. Windows安装Grafana

```
# 下载Grafana for Windows
# https://grafana.com/grafana/download?platform=windows

# 安装后启动服务
net start grafana

# 访问 http://localhost:3000
# 默认用户名/密码：admin/admin
```



### 2. 配置数据源

1. **MySQL数据源**：
   - 名称：CTF Platform MySQL
   - Host：localhost:3306
   - 数据库：ctf_platform
   - 用户：ctf_user
   - 密码：031006
2. **Prometheus数据源**（如果使用）：
   - 名称：Windows Metrics
   - URL：[http://localhost:9090](http://localhost:9090/)

### 3. 创建仪表板

**CTF平台监控仪表板JSON配置**：

```
{
  "dashboard": {
    "title": "CTF平台监控",
    "panels": [
      {
        "title": "CPU使用率",
        "targets": [{
          "expr": "100 - (avg by (instance) (rate(windows_cpu_time_total{mode=\"idle\"}[5m])) * 100)",
          "legendFormat": "{{instance}} CPU"
        }]
      },
      {
        "title": "内存使用",
        "targets": [{
          "expr": "windows_os_physical_memory_free_bytes",
          "legendFormat": "可用内存"
        }]
      },
      {
        "title": "活跃用户数",
        "targets": [{
          "rawSql": "SELECT COUNT(DISTINCT user_id) as active_users FROM submissions WHERE submitted_at > DATE_SUB(NOW(), INTERVAL 1 HOUR)",
          "format": "table"
        }]
      },
      {
        "title": "题目提交趋势",
        "targets": [{
          "rawSql": "SELECT DATE_FORMAT(submitted_at, '%Y-%m-%d %H:00') as hour, COUNT(*) as submissions FROM submissions WHERE submitted_at > DATE_SUB(NOW(), INTERVAL 24 HOUR) GROUP BY hour ORDER BY hour",
          "format": "time_series"
        }]
      }
    ]
  }
}
```



## 📋 监控检查清单

### 每日检查项

- 系统资源使用率（CPU、内存、磁盘）
- 应用日志错误数量
- 数据库连接数
- 网站可访问性
- 备份任务状态

### 每周检查项

- 日志文件大小和轮转
- 数据库性能分析
- 安全事件审查
- 监控告警规则有效性
- 系统更新和补丁

### 每月检查项

- 容量规划评估
- 性能趋势分析
- 安全审计日志
- 监控系统优化
- 备份恢复测试

## 🔧 故障诊断指南

### 快速诊断命令

```
# 1. 检查服务状态
Get-Service CTFPlatform, MySQL

# 2. 检查端口占用
netstat -ano | findstr :5000
netstat -ano | findstr :3306

# 3. 检查日志
Get-Content "C:\CTF-Platform\storage\logs\ctf_platform.log" -Tail 50
Get-Content "C:\ProgramData\MySQL\MySQL Server 8.0\Data\mysql_error.log" -Tail 20

# 4. 检查磁盘空间
Get-PSDrive C | Select-Object Used,Free

# 5. 检查内存使用
Get-Process python | Select-Object PM,CPU

# 6. 测试数据库连接
mysql -u ctf_user -p031006 -e "SELECT 1" ctf_platform

# 7. 测试API端点
Invoke-WebRequest http://localhost:5000/health
Invoke-WebRequest http://localhost:5000/api/v1/challenges
```



### 常见故障处理

| 故障现象       | 可能原因       | 解决方案                |
| :------------- | :------------- | :---------------------- |
| 网站无法访问   | 服务未启动     | `net start CTFPlatform` |
| 数据库连接失败 | MySQL服务停止  | `net start mysql`       |
| 内存使用过高   | 内存泄漏       | 重启Python进程          |
| 磁盘空间不足   | 日志文件过大   | 清理日志，配置轮转      |
| 响应缓慢       | 数据库索引问题 | 优化查询，添加索引      |
| 用户无法登录   | 认证服务异常   | 检查JWT配置和密钥       |

## 📚 日志轮转策略

### 配置日志轮转

创建 `log-rotation.ps1`：

```
# 日志轮转脚本
$LogDir = "C:\CTF-Platform\storage\logs"
$MaxSizeMB = 100  # 单个日志文件最大100MB
$KeepDays = 30    # 保留30天日志

# 轮转应用日志
$AppLog = "$LogDir\ctf_platform.log"
if ((Get-Item $AppLog -ErrorAction SilentlyContinue).Length / 1MB -gt $MaxSizeMB) {
    $Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    Rename-Item $AppLog "$LogDir\ctf_platform-$Timestamp.log"
    
    # 创建新日志文件
    New-Item -ItemType File -Path $AppLog -Force
}

# 清理旧日志
Get-ChildItem "$LogDir\*.log" | Where-Object {
    $_.CreationTime -lt (Get-Date).AddDays(-$KeepDays)
} | Remove-Item -Force

# 清理监控日志
Get-ChildItem "$LogDir\monitoring\*.log" | Where-Object {
    $_.CreationTime -lt (Get-Date).AddDays(-7)
} | Remove-Item -Force
```



### 添加到Windows计划任务

```
# 创建日志轮转任务
$Action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
    -Argument "-File `"C:\CTF-Platform\scripts\log-rotation.ps1`""
$Trigger = New-ScheduledTaskTrigger -Daily -At 2am
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount
$Settings = New-ScheduledTaskSettingsSet

Register-ScheduledTask -TaskName "CTF平台日志轮转" `
    -Action $Action `
    -Trigger $Trigger `
    -Principal $Principal `
    -Settings $Settings
```



## 📈 性能优化建议

### 应用层优化

1. **启用缓存**：使用Redis缓存频繁查询
2. **优化查询**：添加数据库索引
3. **连接池**：配置数据库连接池
4. **静态文件**：使用CDN或Nginx服务静态文件

### 系统层优化

1. **调整MySQL配置**：

   ```
   innodb_buffer_pool_size = 1G
   max_connections = 200
   query_cache_size = 128M
   ```

   

2. **调整Python WSGI服务器**：

   ```
   waitress-serve --threads=8 --host=0.0.0.0 --port=5000 app:app
   ```

   

## 📞 监控支持

### 联系信息

- **系统管理员**：林哲凯
- **数据库管理员**：林文进
- **开发支持**：卢圣轩

### 紧急响应流程

1. 收到告警通知
2. 登录服务器检查状态
3. 根据诊断指南排查问题
4. 执行应急预案
5. 记录故障处理过程
6. 后续优化预防措施

