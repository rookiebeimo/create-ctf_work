# CTF网络安全竞赛平台

一个功能完整的CTF（Capture The Flag）网络安全竞赛平台，支持题目管理、用户认证、积分排行等功能。

## 核心特性

- **完整的CTF功能**：支持Web、Pwn、Reverse、Crypto、Misc等多种题型
- **动态积分系统**：基于解题人数和时间衰减的动态分数计算
- **安全的认证机制**：JWT Token认证，密码哈希存储，权限控制
- **实时排行榜**：全球排行、分类排行、题目排行多维度展示
- **管理员功能**：题目管理、用户管理、分类管理、系统监控
- **详细的提交记录**：记录所有Flag提交，支持统计分析
- **多环境配置**：支持开发、测试、生产环境一键切换

## 快速开始

### 先决条件

- **Python 3.8+** - 后端运行环境
- **MySQL 8.0+** - 数据库服务
- **现代浏览器** - Chrome 90+, Firefox 88+, Edge 90+
- **Git** - 版本控制系统

### Windows 11本地部署

#### 1. 克隆项目

```
git clone https://github.com/ctf-team/ctf-platform.git
cd ctf-platform
```

#### 2. 后端环境设置

```
# 创建虚拟环境（可选但推荐）
python -m venv venv
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

#### 3. 数据库配置

1. 安装MySQL 8.0+
2. 创建数据库和用户：

```
-- 使用MySQL命令行
CREATE DATABASE ctf_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ctf_user'@'localhost' IDENTIFIED BY '031006';
GRANT ALL PRIVILEGES ON ctf_platform.* TO 'ctf_user'@'localhost';
FLUSH PRIVILEGES;
```

#### 4. 初始化数据库

```
# 运行初始化脚本
python init_database.py

# 或者使用Flask命令
flask init-db
```

#### 5. 启动后端服务

```
# 方式1：直接运行
python app.py

# 方式2：使用Flask命令
set FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
```

后端服务将运行在：[http://localhost:5000](http://localhost:5000/)

#### 6. 启动前端服务

前端为静态文件，可以直接使用浏览器打开：

```
# 使用Python内置HTTP服务器
cd frontend
python -m http.server 8000
```

或者直接在浏览器中打开 `frontend/index.html`

#### 7. 访问平台

- 前端地址：[http://localhost:8000](http://localhost:8000/)
- API地址：[http://localhost:5000](http://localhost:5000/)
- 管理员账号：admin / admin123

## 项目结构

```
ctf-platform/
├── backend/                    # 后端代码
│   ├── app.py                 # Flask主应用
│   ├── models.py              # 数据库模型
│   ├── config.py              # 配置文件
│   ├── init_database.py       # 数据库初始化
│   ├── requirements.txt       # Python依赖
│   ├── routes/                # API路由
│   │   ├── auth.py           # 认证相关API
│   │   ├── challenges.py     # 题目相关API
│   │   ├── admin.py          # 管理员API
│   │   ├── submissions.py    # 提交记录API
│   │   └── leaderboard.py    # 排行榜API
│   └── utils/                 # 工具模块
│       ├── auth.py           # 认证工具
│       ├── flag.py           # Flag生成验证
│       ├── scoring.py        # 积分计算
│       └── log.py            # 日志工具
│
├── frontend/                  # 前端代码
│   ├── index.html            # 主页面
│   ├── style.css             # 样式文件
│   ├── app.js                # 主应用逻辑
│   ├── utils.js              # 工具函数
│   ├── auth.js               # 认证模块
│   ├── challenges.js         # 题目模块
│   ├── leaderboard.js        # 排行榜模块
│   └── admin.js              # 管理员模块
│
├── storage/                   # 文件存储
│   ├── challenges/           # 题目附件
│   ├── logs/                 # 系统日志
│   └── temp/                 # 临时文件
├── docs/                      # 项目文档
├── tests/                     # 测试用例
├── .env.example               # 环境变量示例
├── LICENSE                    # 许可证文件
├── CONTRIBUTING.md           # 贡献指南
└── README.md                 # 自述文件
```

## 如何贡献

我们欢迎贡献！请阅读我们的 [贡献指南](https://contributing.md/)。

1. Fork 项目仓库
2. 创建功能分支 (`git checkout -b feat/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feat/amazing-feature`)
5. 开启一个 Pull Request

## 许可证

本项目基于 [MIT](https://license/) 许可证开源。

## 获取帮助

- [提交 Issue](https://github.com/ctf-team/ctf-platform/issues) - 报告Bug或提出新特性
- **团队联系方式**：
  - 项目经理：林哲凯
  - 技术问题：林文进（后端）、卢圣轩（前端）
  - 安全测试：刘城铭
  - 部署运维：杨鹏祥
  - 质量测试：宋礼雄

## 致谢

感谢所有为项目做出贡献的开发者！
