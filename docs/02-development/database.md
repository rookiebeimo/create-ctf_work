# CTF平台数据库指南

## 1. 数据库概述

CTF平台使用MySQL作为主要数据库管理系统，通过SQLAlchemy ORM进行数据访问。数据库设计遵循规范化原则，支持平台的核心功能：用户管理、题目管理、提交记录和排行榜。

## 2. 数据库ER图

### 2.1 实体关系图
![ER图](docs/images/uml/ER图.png)

### 2.2 关系说明

1. **用户-提交**: 一对多关系，一个用户可以有多条提交记录
2. **用户-题目**:
   - 一对多关系（创建者），一个用户可以创建多个题目
   - 一对一关系（首杀者），一个用户可以是题目的首杀者
3. **分类-题目**: 一对多关系，一个分类可以有多个题目
4. **题目-提交**: 一对多关系，一个题目可以有多条提交记录
5. **用户-日志**: 一对多关系，一个用户可以产生多条系统日志

## 3. 数据表详细设计

### 3.1 用户表 (users)

存储用户信息和认证数据。

```
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(64) UNIQUE NOT NULL COMMENT '用户名，唯一',
    email VARCHAR(120) UNIQUE NOT NULL COMMENT '邮箱，唯一',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希值',
    is_admin BOOLEAN DEFAULT FALSE COMMENT '是否管理员',
    score INT DEFAULT 0 COMMENT '用户总积分',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '账户创建时间',
    last_login DATETIME COMMENT '最后登录时间',
    is_active BOOLEAN DEFAULT TRUE COMMENT '账户是否活跃',
    
    -- 索引
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_score (score DESC),
    INDEX idx_created_at (created_at DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';
```



### 3.2 分类表 (categories)

存储题目分类信息。

```
CREATE TABLE categories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(64) UNIQUE NOT NULL COMMENT '分类名称',
    description TEXT COMMENT '分类描述',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='题目分类表';
```



### 3.3 题目表 (challenges)

存储题目信息和元数据。

```
CREATE TABLE challenges (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(128) NOT NULL COMMENT '题目标题',
    description TEXT NOT NULL COMMENT '题目描述',
    flag TEXT NOT NULL COMMENT '正确答案（Flag）',
    points INT NOT NULL DEFAULT 100 COMMENT '题目分值',
    difficulty ENUM('easy', 'medium', 'hard', 'expert') NOT NULL DEFAULT 'medium' COMMENT '难度等级',
    category_id INT NOT NULL COMMENT '分类ID',
    creator_id INT NOT NULL COMMENT '创建者ID',
    solved_count INT DEFAULT 0 COMMENT '已解决人数',
    first_blood_user_id INT COMMENT '首杀用户ID',
    is_hidden BOOLEAN DEFAULT FALSE COMMENT '是否隐藏题目',
    hints TEXT COMMENT '提示信息（JSON格式）',
    attachment_filename VARCHAR(255) COMMENT '附件文件名',
    attachment_url VARCHAR(255) COMMENT '附件URL',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    -- 外键约束
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
    FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (first_blood_user_id) REFERENCES users(id) ON DELETE SET NULL,
    
    -- 索引
    INDEX idx_title (title),
    INDEX idx_category (category_id),
    INDEX idx_difficulty (difficulty),
    INDEX idx_points (points DESC),
    INDEX idx_solved_count (solved_count DESC),
    INDEX idx_created_at (created_at DESC),
    INDEX idx_is_hidden (is_hidden),
    
    -- 复合索引
    INDEX idx_category_difficulty (category_id, difficulty),
    INDEX idx_creator_created (creator_id, created_at DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='题目表';
```



### 3.4 提交记录表 (submissions)

存储用户提交Flag的记录。

```
CREATE TABLE submissions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL COMMENT '用户ID',
    challenge_id INT NOT NULL COMMENT '题目ID',
    flag_submitted TEXT NOT NULL COMMENT '用户提交的Flag',
    is_correct BOOLEAN NOT NULL COMMENT '是否正确',
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '提交时间',
    
    -- 外键约束
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (challenge_id) REFERENCES challenges(id) ON DELETE CASCADE,
    
    -- 索引
    INDEX idx_user_id (user_id),
    INDEX idx_challenge_id (challenge_id),
    INDEX idx_submitted_at (submitted_at DESC),
    INDEX idx_is_correct (is_correct),
    
    -- 复合索引
    INDEX idx_user_challenge (user_id, challenge_id),
    INDEX idx_user_submitted (user_id, submitted_at DESC),
    INDEX idx_challenge_submitted (challenge_id, submitted_at DESC),
    
    -- 唯一约束：确保同一用户对同一题目的正确提交只记录一次
    UNIQUE KEY uk_user_challenge_correct (user_id, challenge_id, is_correct)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='提交记录表';
```



### 3.5 系统日志表 (system_logs)

存储系统操作日志和安全审计日志。

```
CREATE TABLE system_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    level ENUM('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL') NOT NULL DEFAULT 'INFO' COMMENT '日志级别',
    module VARCHAR(64) NOT NULL COMMENT '模块名称',
    message TEXT NOT NULL COMMENT '日志消息',
    user_id INT COMMENT '用户ID（可为空）',
    ip_address VARCHAR(45) COMMENT 'IP地址（支持IPv6）',
    user_agent TEXT COMMENT '用户代理',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    -- 外键约束
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    
    -- 索引
    INDEX idx_level (level),
    INDEX idx_module (module),
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at DESC),
    INDEX idx_ip_address (ip_address),
    
    -- 复合索引
    INDEX idx_module_created (module, created_at DESC),
    INDEX idx_user_created (user_id, created_at DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统日志表';
```



## 4. 数据字典

### 4.1 枚举值定义

#### 难度等级 (difficulty)

```
-- challenges.difficulty 字段枚举值
ENUM('easy', 'medium', 'hard', 'expert')
```



- **easy**: 简单（适合初学者）
- **medium**: 中等（有一定难度）
- **hard**: 困难（需要专业知识）
- **expert**: 专家（非常困难）

#### 日志级别 (level)

```
-- system_logs.level 字段枚举值
ENUM('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
```



- **DEBUG**: 调试信息
- **INFO**: 一般信息
- **WARNING**: 警告信息
- **ERROR**: 错误信息
- **CRITICAL**: 严重错误

### 4.2 业务规则

#### 积分规则

1. 用户积分 = 所有已解决题目的分值之和
2. 重复解决同一题目不重复计分
3. 题目分值可能根据解决人数动态调整

#### Flag验证规则

1. Flag格式: `CTF{...}` 或其他自定义格式
2. 验证方式: 精确匹配或模糊匹配
3. 大小写敏感性: 可配置

#### 提交限制

1. 同一用户对同一题目的正确Flag只记录一次
2. 可以多次提交错误Flag
3. 可配置提交频率限制

## 5. 数据库初始化脚本

### 5.1 完整初始化脚本

```
-- 1. 创建数据库
CREATE DATABASE IF NOT EXISTS ctf_platform
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE ctf_platform;

-- 2. 创建用户表
CREATE TABLE IF NOT EXISTS users (
    -- 表结构如3.1节所示
);

-- 3. 创建分类表
CREATE TABLE IF NOT EXISTS categories (
    -- 表结构如3.2节所示
);

-- 4. 创建题目表
CREATE TABLE IF NOT EXISTS challenges (
    -- 表结构如3.3节所示
);

-- 5. 创建提交记录表
CREATE TABLE IF NOT EXISTS submissions (
    -- 表结构如3.4节所示
);

-- 6. 创建系统日志表
CREATE TABLE IF NOT EXISTS system_logs (
    -- 表结构如3.5节所示
);

-- 7. 插入默认数据

-- 7.1 插入默认分类
INSERT INTO categories (name, description) VALUES
('Web', 'Web安全相关题目，包括SQL注入、XSS、CSRF等漏洞'),
('Pwn', '二进制漏洞利用题目，包括栈溢出、堆利用、格式化字符串等'),
('Reverse', '逆向工程题目，包括软件分析、算法理解、代码还原等'),
('Crypto', '密码学题目，包括古典密码、现代密码、加密算法等'),
('Misc', '杂项题目，包括隐写术、取证、网络协议分析等'),
('Forensics', '数字取证题目，包括日志分析、内存取证、磁盘取证等')
ON DUPLICATE KEY UPDATE description = VALUES(description);

-- 7.2 插入默认管理员用户（密码：admin123）
-- 注意：实际密码需要哈希处理，这里仅为示例
INSERT INTO users (username, email, password_hash, is_admin) VALUES
('admin', 'admin@ctfplatform.com', 
'pbkdf2:sha256:260000$DpS1vP8X$d5c5d1f9e4b6c7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1', 
TRUE)
ON DUPLICATE KEY UPDATE 
    email = VALUES(email),
    password_hash = VALUES(password_hash),
    is_admin = VALUES(is_admin);

-- 8. 创建视图

-- 8.1 用户排行榜视图
CREATE OR REPLACE VIEW user_leaderboard AS
SELECT 
    u.id,
    u.username,
    u.score,
    COUNT(DISTINCT s.challenge_id) AS solved_count,
    MAX(s.submitted_at) AS last_solve
FROM users u
LEFT JOIN submissions s ON u.id = s.user_id AND s.is_correct = TRUE
WHERE u.is_admin = FALSE
GROUP BY u.id, u.username, u.score
ORDER BY u.score DESC, solved_count DESC, last_solve ASC;

-- 8.2 题目统计视图
CREATE OR REPLACE VIEW challenge_statistics AS
SELECT 
    c.id,
    c.title,
    c.category_id,
    cat.name AS category_name,
    c.difficulty,
    c.points,
    c.solved_count,
    COUNT(s.id) AS total_submissions,
    ROUND(COUNT(CASE WHEN s.is_correct THEN 1 END) * 100.0 / NULLIF(COUNT(s.id), 0), 2) AS success_rate,
    MIN(s.submitted_at) AS first_solve_time,
    u.username AS first_blood_user
FROM challenges c
JOIN categories cat ON c.category_id = cat.id
LEFT JOIN submissions s ON c.id = s.challenge_id
LEFT JOIN users u ON c.first_blood_user_id = u.id
GROUP BY c.id, c.title, c.category_id, cat.name, c.difficulty, c.points, c.solved_count, u.username;

-- 9. 创建存储过程

-- 9.1 更新用户积分存储过程
DELIMITER //
CREATE PROCEDURE update_user_score(IN user_id INT)
BEGIN
    DECLARE total_score INT;
    
    -- 计算用户总积分（只计算正确的提交，且每个题目只计算一次）
    SELECT SUM(DISTINCT c.points) INTO total_score
    FROM submissions s
    JOIN challenges c ON s.challenge_id = c.id
    WHERE s.user_id = user_id AND s.is_correct = TRUE;
    
    -- 更新用户积分
    UPDATE users 
    SET score = COALESCE(total_score, 0)
    WHERE id = user_id;
END //
DELIMITER ;

-- 9.2 更新题目解决人数存储过程
DELIMITER //
CREATE PROCEDURE update_challenge_solved_count(IN challenge_id INT)
BEGIN
    DECLARE solved_count INT;
    DECLARE first_blood_user_id INT;
    
    -- 计算解决人数
    SELECT COUNT(DISTINCT user_id) INTO solved_count
    FROM submissions
    WHERE challenge_id = challenge_id AND is_correct = TRUE;
    
    -- 获取首杀用户
    SELECT user_id INTO first_blood_user_id
    FROM submissions
    WHERE challenge_id = challenge_id AND is_correct = TRUE
    ORDER BY submitted_at ASC
    LIMIT 1;
    
    -- 更新题目信息
    UPDATE challenges 
    SET 
        solved_count = solved_count,
        first_blood_user_id = first_blood_user_id
    WHERE id = challenge_id;
END //
DELIMITER ;

-- 10. 创建触发器

-- 10.1 插入提交记录后更新用户积分
DELIMITER //
CREATE TRIGGER after_submission_insert
AFTER INSERT ON submissions
FOR EACH ROW
BEGIN
    -- 如果提交正确，更新用户积分
    IF NEW.is_correct = TRUE THEN
        CALL update_user_score(NEW.user_id);
        CALL update_challenge_solved_count(NEW.challenge_id);
    END IF;
END //
DELIMITER ;

-- 10.2 更新提交记录后更新用户积分
DELIMITER //
CREATE TRIGGER after_submission_update
AFTER UPDATE ON submissions
FOR EACH ROW
BEGIN
    -- 如果正确状态发生变化
    IF OLD.is_correct != NEW.is_correct THEN
        CALL update_user_score(NEW.user_id);
        CALL update_challenge_solved_count(NEW.challenge_id);
    END IF;
END //
DELIMITER ;

-- 10.3 删除提交记录后更新用户积分
DELIMITER //
CREATE TRIGGER after_submission_delete
AFTER DELETE ON submissions
FOR EACH ROW
BEGIN
    -- 如果删除的是正确提交
    IF OLD.is_correct = TRUE THEN
        CALL update_user_score(OLD.user_id);
        CALL update_challenge_solved_count(OLD.challenge_id);
    END IF;
END //
DELIMITER ;
```



### 5.2 Python初始化脚本

参考 `init_database.py` 文件：

```
#!/usr/bin/env python3
"""
数据库初始化脚本
在首次部署时运行此脚本创建数据库和表
"""

import os
import sys
from flask import Flask
from models import db, init_db

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_app():
    """创建Flask应用实例"""
    app = Flask(__name__)
    
    # 配置
    from config import get_config
    app.config.from_object(get_config())
    
    return app

def main():
    """主函数"""
    print("正在初始化CTF平台数据库...")
    
    # 创建应用实例
    app = create_app()
    
    # 初始化数据库
    with app.app_context():
        init_db(app)
        print("数据库初始化完成！")
        
        # 显示创建的表
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"创建的表: {', '.join(tables)}")
        
        # 显示默认分类
        from models import Category, User
        categories = Category.query.all()
        print(f"默认分类: {[cat.name for cat in categories]}")
        
        # 显示管理员用户
        admin_users = User.query.filter_by(is_admin=True).all()
        print(f"管理员用户: {[user.username for user in admin_users]}")

if __name__ == '__main__':
    main()
```



## 6. 数据库迁移管理

### 6.1 使用Flask-Migrate

#### 初始化迁移环境

```
# 安装Flask-Migrate（已在requirements.txt中）
pip install flask-migrate

# 初始化迁移仓库
flask db init

# 创建第一个迁移
flask db migrate -m "Initial migration"

# 应用迁移
flask db upgrade
```



#### 创建新迁移

```
# 1. 修改数据模型（models.py）
# 2. 生成迁移脚本
flask db migrate -m "Add new_column to users table"

# 3. 检查生成的迁移脚本
# 查看 migrations/versions/ 目录下的新文件

# 4. 应用迁移
flask db upgrade

# 5. 验证迁移
flask db current
```



### 6.2 手动迁移脚本示例

#### 添加新字段

```
-- 迁移脚本: 001_add_last_active_to_users.sql
-- 描述：为用户表添加 last_active 字段

-- 向上迁移
ALTER TABLE users 
ADD COLUMN last_active DATETIME NULL COMMENT '最后活跃时间' 
AFTER last_login;

CREATE INDEX idx_last_active ON users(last_active DESC);

-- 向下迁移（回滚）
-- ALTER TABLE users DROP COLUMN last_active;
```



#### 修改表结构

```
-- 迁移脚本: 002_add_contest_support.sql
-- 描述：添加比赛支持相关表

-- 创建比赛表
CREATE TABLE contests (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(128) NOT NULL COMMENT '比赛名称',
    description TEXT COMMENT '比赛描述',
    start_time DATETIME NOT NULL COMMENT '开始时间',
    end_time DATETIME NOT NULL COMMENT '结束时间',
    is_public BOOLEAN DEFAULT TRUE COMMENT '是否公开',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_start_time (start_time),
    INDEX idx_end_time (end_time),
    INDEX idx_is_public (is_public)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建比赛-题目关联表
CREATE TABLE contest_challenges (
    contest_id INT NOT NULL,
    challenge_id INT NOT NULL,
    display_order INT DEFAULT 0 COMMENT '显示顺序',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (contest_id, challenge_id),
    FOREIGN KEY (contest_id) REFERENCES contests(id) ON DELETE CASCADE,
    FOREIGN KEY (challenge_id) REFERENCES challenges(id) ON DELETE CASCADE,
    
    INDEX idx_display_order (display_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```



## 7. 数据库优化

### 7.1 索引优化策略

#### 查询分析

```
-- 查看慢查询
SHOW VARIABLES LIKE 'slow_query_log';
SHOW VARIABLES LIKE 'long_query_time';

-- 分析查询执行计划
EXPLAIN SELECT * FROM users WHERE username = 'admin';

-- 查看索引使用情况
SHOW INDEX FROM users;
```



#### 建议的索引

```
-- 1. 用户相关查询优化
CREATE INDEX idx_users_score_admin ON users(score DESC, is_admin);

-- 2. 提交记录查询优化
CREATE INDEX idx_submissions_user_correct ON submissions(user_id, is_correct, submitted_at DESC);

-- 3. 题目查询优化
CREATE INDEX idx_challenges_category_hidden ON challenges(category_id, is_hidden, difficulty, points DESC);

-- 4. 排行榜查询优化
CREATE INDEX idx_users_score_solved ON users(score DESC, (SELECT COUNT(*) FROM submissions WHERE user_id = users.id AND is_correct = TRUE) DESC);
```



### 7.2 查询优化示例

#### 优化前

```
-- 低效查询：使用子查询
SELECT * FROM users 
WHERE id IN (SELECT user_id FROM submissions WHERE is_correct = TRUE);
```



#### 优化后

```
-- 高效查询：使用JOIN
SELECT DISTINCT u.* FROM users u
JOIN submissions s ON u.id = s.user_id
WHERE s.is_correct = TRUE;

-- 或使用EXISTS
SELECT * FROM users u
WHERE EXISTS (
    SELECT 1 FROM submissions s 
    WHERE s.user_id = u.id AND s.is_correct = TRUE
);
```



### 7.3 分区策略（大型数据集）

#### 按时间分区

```
-- 对提交记录表按月份分区
ALTER TABLE submissions 
PARTITION BY RANGE (YEAR(submitted_at) * 100 + MONTH(submitted_at)) (
    PARTITION p202401 VALUES LESS THAN (202402),
    PARTITION p202402 VALUES LESS THAN (202403),
    PARTITION p202403 VALUES LESS THAN (202404),
    PARTITION p202404 VALUES LESS THAN (202405),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);
```



## 8. 数据备份和恢复

### 8.1 备份策略

#### 完整备份脚本

```
#!/bin/bash
# backup_database.sh

BACKUP_DIR="/var/backup/mysql"
DB_NAME="ctf_platform"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_${DATE}.sql.gz"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 执行备份
mysqldump --single-transaction --routines --triggers \
    --databases $DB_NAME | gzip > $BACKUP_FILE

# 记录备份信息
echo "备份完成: $BACKUP_FILE" >> $BACKUP_DIR/backup.log
echo "文件大小: $(du -h $BACKUP_FILE | cut -f1)" >> $BACKUP_DIR/backup.log

# 清理旧备份（保留30天）
find $BACKUP_DIR -name "${DB_NAME}_*.sql.gz" -mtime +30 -delete
```



#### 增量备份

```
#!/bin/bash
# incremental_backup.sh

BACKUP_DIR="/var/backup/mysql/incremental"
DB_NAME="ctf_platform"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 刷新二进制日志
mysql -e "FLUSH BINARY LOGS;"

# 备份二进制日志
cp /var/lib/mysql/mysql-bin.* $BACKUP_DIR/

echo "增量备份完成: $DATE" >> $BACKUP_DIR/incremental.log
```



### 8.2 恢复策略

#### 完整恢复

```
#!/bin/bash
# restore_database.sh

BACKUP_FILE="$1"
DB_NAME="ctf_platform"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "错误: 备份文件不存在"
    exit 1
fi

# 停止相关服务
systemctl stop ctf-platform

# 恢复数据库
gunzip -c $BACKUP_FILE | mysql $DB_NAME

# 重启服务
systemctl start ctf-platform

echo "数据库恢复完成: $BACKUP_FILE"
```



#### 时间点恢复

```
#!/bin/bash
# point_in_time_restore.sh

BACKUP_FILE="$1"
RECOVERY_TIME="$2"  # 格式: '2024-01-01 12:00:00'

# 恢复完整备份
gunzip -c $BACKUP_FILE | mysql ctf_platform

# 应用二进制日志
mysqlbinlog --start-datetime="$RECOVERY_TIME" \
    /var/lib/mysql/mysql-bin.* | mysql ctf_platform

echo "时间点恢复完成到: $RECOVERY_TIME"
```



## 9. 监控和维护

### 9.1 监控查询

#### 数据库状态

```
-- 查看连接数
SHOW STATUS LIKE 'Threads_connected';
SHOW VARIABLES LIKE 'max_connections';

-- 查看查询缓存
SHOW STATUS LIKE 'Qcache%';

-- 查看表空间使用
SELECT 
    table_schema AS '数据库',
    table_name AS '表名',
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS '大小(MB)'
FROM information_schema.tables
WHERE table_schema = 'ctf_platform'
ORDER BY (data_length + index_length) DESC;

-- 查看索引使用情况
SELECT 
    object_schema,
    object_name,
    index_name,
    COUNT_READ,
    COUNT_FETCH,
    COUNT_INSERT,
    COUNT_UPDATE,
    COUNT_DELETE
FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE object_schema = 'ctf_platform'
ORDER BY COUNT_READ DESC;
```



#### 性能监控

```
-- 查看慢查询
SELECT 
    query_time,
    lock_time,
    rows_sent,
    rows_examined,
    db,
    last_insert_id,
    insert_id,
    server_id,
    sql_text
FROM mysql.slow_log
ORDER BY query_time DESC
LIMIT 10;

-- 查看当前连接和执行查询
SHOW PROCESSLIST;

-- 查看锁状态
SHOW ENGINE INNODB STATUS;
```



### 9.2 维护任务

#### 定期优化表

```
-- 优化表（碎片整理）
OPTIMIZE TABLE users, challenges, submissions;

-- 分析表（更新统计信息）
ANALYZE TABLE users, challenges, submissions;

-- 修复表（如果损坏）
REPAIR TABLE users;
```



#### 清理历史数据

```
-- 清理旧的提交记录（保留6个月）
DELETE FROM submissions 
WHERE submitted_at < DATE_SUB(NOW(), INTERVAL 6 MONTH);

-- 清理系统日志（保留3个月）
DELETE FROM system_logs 
WHERE created_at < DATE_SUB(NOW(), INTERVAL 3 MONTH);

-- 清理非活跃用户（1年未登录）
UPDATE users 
SET is_active = FALSE 
WHERE last_login < DATE_SUB(NOW(), INTERVAL 1 YEAR) 
AND is_admin = FALSE;
```



## 10. 安全考虑

### 10.1 访问控制

```
-- 创建只读用户用于报表
CREATE USER 'ctf_report'@'localhost' IDENTIFIED BY 'report_password';
GRANT SELECT ON ctf_platform.* TO 'ctf_report'@'localhost';

-- 创建备份用户
CREATE USER 'ctf_backup'@'localhost' IDENTIFIED BY 'backup_password';
GRANT SELECT, RELOAD, LOCK TABLES ON *.* TO 'ctf_backup'@'localhost';

-- 限制用户连接数
ALTER USER 'ctf_user'@'localhost' WITH MAX_USER_CONNECTIONS 10;
```



### 10.2 数据加密

```
-- 启用SSL连接
GRANT USAGE ON *.* TO 'ctf_user'@'localhost' REQUIRE SSL;

-- 加密敏感数据（建议在应用层实现）
-- 密码字段已使用bcrypt哈希
-- Flag字段可以加密存储
```



### 10.3 审计日志

```
-- 启用通用查询日志
SET GLOBAL general_log = 'ON';
SET GLOBAL log_output = 'TABLE';

-- 查看审计日志
SELECT * FROM mysql.general_log 
WHERE argument LIKE '%DELETE%' OR argument LIKE '%UPDATE%'
ORDER BY event_time DESC;
```



## 11. 故障排除

### 11.1 常见问题

#### 问题1: 外键约束失败

```
错误：Cannot add or update a child row: a foreign key constraint fails
```



**解决方案**：

```
-- 1. 检查外键数据是否存在
SELECT * FROM categories WHERE id = 999;

-- 2. 临时禁用外键检查
SET FOREIGN_KEY_CHECKS = 0;
-- 执行操作
SET FOREIGN_KEY_CHECKS = 1;

-- 3. 修复数据一致性
-- 添加缺失的父记录或删除无效的子记录
```



#### 问题2: 表锁等待超时

```
错误：Lock wait timeout exceeded; try restarting transaction
```



**解决方案**：

```
-- 1. 查看当前锁
SHOW ENGINE INNODB STATUS;

-- 2. 查看锁等待
SELECT * FROM information_schema.INNODB_LOCKS;
SELECT * FROM information_schema.INNODB_LOCK_WAITS;

-- 3. 杀死阻塞的进程
SHOW PROCESSLIST;
KILL <process_id>;

-- 4. 增加锁等待超时时间
SET GLOBAL innodb_lock_wait_timeout = 120;
```



#### 问题3: 连接数过多

```
错误：Too many connections
```



**解决方案**：

```
-- 1. 查看当前连接数
SHOW STATUS LIKE 'Threads_connected';

-- 2. 增加最大连接数
SET GLOBAL max_connections = 500;

-- 3. 优化连接池设置
-- 在应用中配置合适的连接池大小
```



### 11.2 性能问题诊断

#### 诊断步骤

```
# 1. 检查系统资源
top -c
free -h
iostat -x 1

# 2. 检查MySQL状态
mysqladmin -u root -p status
mysqladmin -u root -p extended-status

# 3. 分析慢查询日志
mysqldumpslow /var/log/mysql/slow.log
```



#### 性能优化检查表

1. ✅ 所有查询都使用索引
2. ✅ 没有全表扫描
3. ✅ 连接查询优化
4. ✅ 查询缓存配置合理
5. ✅ 内存配置适当
6. ✅ 定期维护表

------

**数据库指南总结**：

1. **设计规范**: 遵循数据库设计三范式，建立合适的关系
2. **性能优化**: 合理的索引策略和查询优化
3. **安全可靠**: 完善的备份恢复和访问控制
4. **易于维护**: 详细的文档和监控方案
5. **可扩展性**: 支持数据增长和架构演进

通过遵循本指南，您可以有效地管理和维护CTF平台的数据库系统，确保数据的安全性、完整性和高性能访问。