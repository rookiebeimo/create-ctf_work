# CTF平台API接口文档

## 📋 文档信息

| 项目名称     | CTF网络安全竞赛平台            |
| ------------ | ------------------------------ |
| 接口版本     | v1.1                           |
| 基础URL      | `http://localhost:5000/api/v1` |
| 文档版本     | 1.0.0                          |
| **更新日期** | **2025年10月15日**             |

## 1. 概述

### 1.1 接口规范
- 所有接口使用RESTful风格设计
- 数据格式：JSON
- 字符编码：UTF-8
- 时区：UTC

### 1.2 认证机制
使用JWT Token进行身份认证，Token需要在请求头中携带：
```http
Authorization: Bearer L1BU0vHwj0NwS75duJ5EB1eiEGMw1GDj2FOOeI2hn46rfDAbvJB08qOBi0KgfqLg
```

### 1.3 状态码说明
| 状态码 | 说明              |
| ------ | ----------------- |
| 200    | 请求成功          |
| 201    | 创建成功          |
| 400    | 请求参数错误      |
| 401    | 未授权或Token无效 |
| 403    | 权限不足          |
| 404    | 资源不存在        |
| 500    | 服务器内部错误    |

### 1.4 公共响应格式
```json
{
  "message": "操作结果描述",
  "data": {}, // 成功时返回的数据
  "error": "错误详情" // 失败时返回的错误信息
}
```

## 2. 认证模块

### 2.1 用户注册

**接口描述**：新用户注册

**请求方法**：POST

**接口路径**：`/auth/register`

**请求头**：
```http
Content-Type: application/json
```

**请求体**：
```json
{
  "username": "string, 用户名，必填",
  "email": "string, 邮箱地址，必填",
  "password": "string, 密码，必填"
}
```

**成功响应**（201）：
```json
{
  "message": "User registered successfully!",
  "user_id": 1
}
```

**错误响应**（400）：
```json
{
  "message": "Username already exists!"
}
```

**示例**：
```bash
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'
```

### 2.2 用户登录

**接口描述**：用户登录获取JWT Token

**请求方法**：POST

**接口路径**：`/auth/login`

**请求头**：
```http
Content-Type: application/json
```

**请求体**：
```json
{
  "username": "string, 用户名，必填",
  "password": "string, 密码，必填"
}
```

**成功响应**（200）：
```json
{
  "message": "Login successful!",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "is_admin": false,
    "score": 0
  }
}
```

**错误响应**（401）：
```json
{
  "message": "Invalid credentials!"
}
```

**示例**：
```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'
```

### 2.3 获取用户资料

**接口描述**：获取当前登录用户的资料信息

**请求方法**：GET

**接口路径**：`/auth/profile`

**请求头**：
```http
Authorization: Bearer L1BU0vHwj0NwS75duJ5EB1eiEGMw1GDj2FOOeI2hn46rfDAbvJB08qOBi0KgfqLg
Content-Type: application/json
```

**成功响应**（200）：
```json
{
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "is_admin": false,
    "created_at": "2025-10-15T08:30:00Z",
    "score": 100
  }
}
```

**示例**：
```bash
curl -X GET http://localhost:5000/api/v1/auth/profile \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 2.4 更新用户资料

**接口描述**：更新当前登录用户的资料

**请求方法**：PUT

**接口路径**：`/auth/profile`

**请求头**：
```http
Authorization: Bearer L1BU0vHwj0NwS75duJ5EB1eiEGMw1GDj2FOOeI2hn46rfDAbvJB08qOBi0KgfqLg
Content-Type: application/json
```

**请求体**：
```json
{
  "email": "string, 新邮箱地址，可选",
  "password": "string, 新密码，可选"
}
```

**成功响应**（200）：
```json
{
  "message": "Profile updated successfully!"
}
```

**示例**：
```bash
curl -X PUT http://localhost:5000/api/v1/auth/profile \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"email":"newemail@example.com"}'
```

## 3. 题目管理模块

### 3.1 获取题目列表

**接口描述**：获取所有可见的题目列表（管理员可以看到所有题目，包括隐藏的）

**请求方法**：GET

**接口路径**：`/challenges`

**请求头**：
```http
Authorization: Bearer L1BU0vHwj0NwS75duJ5EB1eiEGMw1GDj2FOOeI2hn46rfDAbvJB08qOBi0KgfqLg
```

**查询参数**：
| 参数名     | 类型    | 必填 | 说明                  |
| ---------- | ------- | ---- | --------------------- |
| category   | string  | 否   | 按分类筛选            |
| difficulty | string  | 否   | 按难度筛选            |
| solved     | boolean | 否   | 筛选已解决/未解决题目 |

**成功响应**（200）：
```json
{
  "challenges": [
    {
      "id": 1,
      "title": "SQL注入挑战",
      "description": "这是一道SQL注入题目...",
      "category": "Web",
      "category_id": 1,
      "difficulty": "medium",
      "points": 100,
      "solved_count": 15,
      "is_solved": false,
      "is_hidden": false,
      "created_at": "2025-10-15T08:30:00Z",
      "hints": ["提示1", "提示2"]
    }
  ]
}
```

**示例**：
```bash
curl -X GET "http://localhost:5000/api/v1/challenges?category=Web&difficulty=medium" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 3.2 获取单个题目详情

**接口描述**：获取指定题目的详细信息

**请求方法**：GET

**接口路径**：`/challenges/{id}`

**路径参数**：
| 参数名 | 类型    | 必填 | 说明   |
| ------ | ------- | ---- | ------ |
| id     | integer | 是   | 题目ID |

**请求头**：
```http
Authorization: Bearer L1BU0vHwj0NwS75duJ5EB1eiEGMw1GDj2FOOeI2hn46rfDAbvJB08qOBi0KgfqLg
```

**成功响应**（200）：
```json
{
  "challenge": {
    "id": 1,
    "title": "SQL注入挑战",
    "description": "这是一道SQL注入题目...",
    "category": "Web",
    "category_id": 1,
    "difficulty": "medium",
    "points": 100,
    "solved_count": 15,
    "is_solved": false,
    "is_hidden": false,
    "created_at": "2025-10-15T08:30:00Z",
    "updated_at": "2025-10-15T08:30:00Z",
    "hints": ["提示1", "提示2"],
    "attachment_filename": "challenge.zip",
    "attachment_url": "/api/v1/challenges/1/download"
  }
}
```

**示例**：
```bash
curl -X GET http://localhost:5000/api/v1/challenges/1 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 3.3 提交Flag

**接口描述**：提交题目Flag进行验证

**请求方法**：POST

**接口路径**：`/challenges/{id}/submit`

**路径参数**：
| 参数名 | 类型    | 必填 | 说明   |
| ------ | ------- | ---- | ------ |
| id     | integer | 是   | 题目ID |

**请求头**：
```http
Authorization: Bearer L1BU0vHwj0NwS75duJ5EB1eiEGMw1GDj2FOOeI2hn46rfDAbvJB08qOBi0KgfqLg
Content-Type: application/json
```

**请求体**：
```json
{
  "flag": "string, 提交的Flag，必填"
}
```

**成功响应**（200）：
```json
{
  "message": "Correct flag!",
  "is_correct": true
}
```

**错误响应**（200）：
```json
{
  "message": "Incorrect flag!",
  "is_correct": false
}
```

**示例**：
```bash
curl -X POST http://localhost:5000/api/v1/challenges/1/submit \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"flag":"CTF{test_flag}"}'
```

### 3.4 创建题目（管理员）

**接口描述**：创建新题目（仅管理员）

**请求方法**：POST

**接口路径**：`/challenges`

**请求头**：
```http
Authorization: Bearer L1BU0vHwj0NwS75duJ5EB1eiEGMw1GDj2FOOeI2hn46rfDAbvJB08qOBi0KgfqLg
Content-Type: application/json
```

**请求体**：
```json
{
  "title": "string, 题目标题，必填",
  "description": "string, 题目描述，必填",
  "flag": "string, 正确Flag，必填",
  "points": "integer, 题目分数，必填",
  "difficulty": "string, 难度(easy/medium/hard/expert)，必填",
  "category_id": "integer, 分类ID，必填",
  "hints": ["string, 提示列表，可选"],
  "is_hidden": "boolean, 是否隐藏，默认false"
}
```

**成功响应**（201）：
```json
{
  "message": "题目创建成功!",
  "challenge_id": 2,
  "challenge": {
    "id": 2,
    "title": "新题目",
    "points": 100,
    "difficulty": "medium"
  }
}
```

**示例**：
```bash
curl -X POST http://localhost:5000/api/v1/challenges \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "XSS挑战",
    "description": "这是一道XSS题目",
    "flag": "CTF{xss_challenge}",
    "points": 150,
    "difficulty": "hard",
    "category_id": 1,
    "hints": ["注意DOM XSS"],
    "is_hidden": false
  }'
```

### 3.5 更新题目（管理员）

**接口描述**：更新题目信息（仅管理员）

**请求方法**：PUT

**接口路径**：`/challenges/{id}`

**路径参数**：
| 参数名 | 类型    | 必填 | 说明   |
| ------ | ------- | ---- | ------ |
| id     | integer | 是   | 题目ID |

**请求头**：
```http
Authorization: Bearer L1BU0vHwj0NwS75duJ5EB1eiEGMw1GDj2FOOeI2hn46rfDAbvJB08qOBi0KgfqLg
Content-Type: application/json
```

**请求体**：
```json
{
  "title": "string, 题目标题，可选",
  "description": "string, 题目描述，可选",
  "flag": "string, 正确Flag，可选",
  "points": "integer, 题目分数，可选",
  "difficulty": "string, 难度，可选",
  "category_id": "integer, 分类ID，可选",
  "hints": ["string, 提示列表，可选"],
  "is_hidden": "boolean, 是否隐藏，可选"
}
```

**成功响应**（200）：
```json
{
  "message": "Challenge updated successfully!"
}
```

**示例**：
```bash
curl -X PUT http://localhost:5000/api/v1/challenges/2 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "points": 200,
    "difficulty": "expert"
  }'
```

### 3.6 删除题目（管理员）

**接口描述**：删除题目（仅管理员）

**请求方法**：DELETE

**接口路径**：`/challenges/{id}`

**路径参数**：
| 参数名 | 类型    | 必填 | 说明   |
| ------ | ------- | ---- | ------ |
| id     | integer | 是   | 题目ID |

**请求头**：
```http
Authorization: Bearer L1BU0vHwj0NwS75duJ5EB1eiEGMw1GDj2FOOeI2hn46rfDAbvJB08qOBi0KgfqLg
```

**成功响应**（200）：
```json
{
  "message": "Challenge deleted successfully!"
}
```

**示例**：
```bash
curl -X DELETE http://localhost:5000/api/v1/challenges/2 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 3.7 下载题目附件

**接口描述**：下载题目附件文件

**请求方法**：GET

**接口路径**：`/challenges/{id}/download`

**路径参数**：
| 参数名 | 类型    | 必填 | 说明   |
| ------ | ------- | ---- | ------ |
| id     | integer | 是   | 题目ID |

**请求头**：
```http
Authorization: Bearer L1BU0vHwj0NwS75duJ5EB1eiEGMw1GDj2FOOeI2hn46rfDAbvJB08qOBi0KgfqLg
```

**成功响应**：返回文件流

**示例**：
```bash
curl -X GET http://localhost:5000/api/v1/challenges/1/download \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -o challenge.zip
```

### 3.8 获取分类列表

**接口描述**：获取所有题目分类

**请求方法**：GET

**接口路径**：`/categories`

**请求头**：
```http
Authorization: Bearer L1BU0vHwj0NwS75duJ5EB1eiEGMw1GDj2FOOeI2hn46rfDAbvJB08qOBi0KgfqLg
```

**成功响应**（200）：
```json
{
  "categories": [
    {
      "id": 1,
      "name": "Web",
      "description": "Web安全相关题目",
      "created_at": "2025-10-15T08:30:00Z"
    },
    {
      "id": 2,
      "name": "Pwn",
      "description": "二进制漏洞利用题目",
      "created_at": "2025-10-15T08:30:00Z"
    }
  ]
}
```

**示例**：
```bash
curl -X GET http://localhost:5000/api/v1/categories \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## 4. 排行榜模块

### 4.1 获取全球排行榜

**接口描述**：获取所有用户的积分排行榜

**请求方法**：GET

**接口路径**：`/leaderboard`

**请求头**：
```http
Authorization: Bearer L1BU0vHwj0NwS75duJ5EB1eiEGMw1GDj2FOOeI2hn46rfDAbvJB08qOBi0KgfqLg
```

**查询参数**：
| 参数名   | 类型    | 必填 | 说明             |
| -------- | ------- | ---- | ---------------- |
| page     | integer | 否   | 页码，默认1      |
| per_page | integer | 否   | 每页数量，默认50 |

**成功响应**（200）：
```json
{
  "leaderboard": [
    {
      "rank": 1,
      "user_id": 3,
      "username": "topuser",
      "score": 1500,
      "solved_count": 15,
      "last_solve": "2025-10-20T10:30:00Z"
    },
    {
      "rank": 2,
      "user_id": 1,
      "username": "testuser",
      "score": 1200,
      "solved_count": 12,
      "last_solve": "2025-10-19T14:20:00Z"
    }
  ],
  "total": 150,
  "pages": 3,
  "current_page": 1
}
```

**示例**：
```bash
curl -X GET "http://localhost:5000/api/v1/leaderboard?page=1&per_page=20" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 4.2 获取分类排行榜

**接口描述**：获取指定分类的排行榜

**请求方法**：GET

**接口路径**：`/leaderboard/category/{category_id}`

**路径参数**：
| 参数名      | 类型    | 必填 | 说明   |
| ----------- | ------- | ---- | ------ |
| category_id | integer | 是   | 分类ID |

**请求头**：
```http
Authorization: Bearer L1BU0vHwj0NwS75duJ5EB1eiEGMw1GDj2FOOeI2hn46rfDAbvJB08qOBi0KgfqLg
```

**成功响应**（200）：
```json
{
  "category_id": 1,
  "leaderboard": [
    {
      "rank": 1,
      "user_id": 3,
      "username": "topuser",
      "score": 500,
      "solved_count": 5
    },
    {
      "rank": 2,
      "user_id": 1,
      "username": "testuser",
      "score": 300,
      "solved_count": 3
    }
  ]
}
```

**示例**：
```bash
curl -X GET http://localhost:5000/api/v1/leaderboard/category/1 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 4.3 获取题目排行榜

**接口描述**：获取指定题目的解题排行榜

**请求方法**：GET

**接口路径**：`/leaderboard/challenge/{challenge_id}`

**路径参数**：
| 参数名       | 类型    | 必填 | 说明   |
| ------------ | ------- | ---- | ------ |
| challenge_id | integer | 是   | 题目ID |

**请求头**：
```http
Authorization: Bearer L1BU0vHwj0NwS75duJ5EB1eiEGMw1GDj2FOOeI2hn46rfDAbvJB08qOBi0KgfqLg
```

**成功响应**（200）：
```json
{
  "challenge_id": 1,
  "leaderboard": [
    {
      "rank": 1,
      "user_id": 3,
      "username": "firstblood",
      "solved_at": "2025-10-15T09:00:00Z"
    },
    {
      "rank": 2,
      "user_id": 5,
      "username": "second",
      "solved_at": "2025-10-15T09:30:00Z"
    }
  ]
}
```

**示例**：
```bash
curl -X GET http://localhost:5000/api/v1/leaderboard/challenge/1 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## 5. 提交记录模块

### 5.1 获取提交记录列表

**接口描述**：获取提交记录列表（管理员可查看所有，用户只能查看自己的）

**请求方法**：GET

**接口路径**：`/submissions`

**请求头**：
```http
Authorization: Bearer L1BU0vHwj0NwS75duJ5EB1eiEGMw1GDj2FOOeI2hn46rfDAbvJB08qOBi0KgfqLg
```

**查询参数**：
| 参数名       | 类型    | 必填 | 说明                         |
| ------------ | ------- | ---- | ---------------------------- |
| page         | integer | 否   | 页码，默认1                  |
| per_page     | integer | 否   | 每页数量，默认20             |
| challenge_id | integer | 否   | 按题目ID筛选                 |
| user_id      | integer | 否   | 按用户ID筛选（仅管理员可用） |

**成功响应**（200）：
```json
{
  "submissions": [
    {
      "id": 1,
      "user_id": 1,
      "username": "testuser",
      "challenge_id": 1,
      "challenge_title": "SQL注入挑战",
      "flag_submitted": "CTF{test_flag}",
      "is_correct": true,
      "submitted_at": "2025-10-15T10:30:00Z"
    }
  ],
  "total": 100,
  "pages": 5,
  "current_page": 1
}
```

**示例**：
```bash
curl -X GET "http://localhost:5000/api/v1/submissions?challenge_id=1&page=1" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 5.2 获取用户提交记录

**接口描述**：获取指定用户的提交记录

**请求方法**：GET

**接口路径**：`/submissions/user/{user_id}`

**路径参数**：
| 参数名  | 类型    | 必填 | 说明   |
| ------- | ------- | ---- | ------ |
| user_id | integer | 是   | 用户ID |

**请求头**：
```http
Authorization: Bearer L1BU0vHwj0NwS75duJ5EB1eiEGMw1GDj2FOOeI2hn46rfDAbvJB08qOBi0KgfqLg
```

**查询参数**：
| 参数名   | 类型    | 必填 | 说明             |
| -------- | ------- | ---- | ---------------- |
| page     | integer | 否   | 页码，默认1      |
| per_page | integer | 否   | 每页数量，默认20 |

**成功响应**（200）：
```json
{
  "submissions": [
    {
      "id": 1,
      "challenge_id": 1,
      "challenge_title": "SQL注入挑战",
      "is_correct": true,
      "submitted_at": "2025-10-15T10:30:00Z"
    }
  ],
  "total": 50,
  "pages": 3,
  "current_page": 1
}
```

**示例**：
```bash
curl -X GET "http://localhost:5000/api/v1/submissions/user/1?page=1" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 5.3 获取题目提交记录

**接口描述**：获取指定题目的提交记录

**请求方法**：GET

**接口路径**：`/submissions/challenge/{challenge_id}`

**路径参数**：
| 参数名       | 类型    | 必填 | 说明   |
| ------------ | ------- | ---- | ------ |
| challenge_id | integer | 是   | 题目ID |

**请求头**：
```http
Authorization: Bearer L1BU0vHwj0NwS75duJ5EB1eiEGMw1GDj2FOOeI2hn46rfDAbvJB08qOBi0KgfqLg
```

**查询参数**：
| 参数名   | 类型    | 必填 | 说明             |
| -------- | ------- | ---- | ---------------- |
| page     | integer | 否   | 页码，默认1      |
| per_page | integer | 否   | 每页数量，默认20 |

**成功响应**（200）：
```json
{
  "submissions": [
    {
      "id": 1,
      "user_id": 1,
      "username": "testuser",
      "is_correct": true,
      "submitted_at": "2025-10-15T10:30:00Z"
    }
  ],
  "total": 25,
  "pages": 2,
  "current_page": 1
}
```

**示例**：
```bash
curl -X GET "http://localhost:5000/api/v1/submissions/challenge/1?page=1" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 5.4 获取提交统计

**接口描述**：获取提交统计数据

**请求方法**：GET

**接口路径**：`/submissions/stats`

**请求头**：
```http
Authorization: Bearer L1BU0vHwj0NwS75duJ5EB1eiEGMw1GDj2FOOeI2hn46rfDAbvJB08qOBi0KgfqLg
```

**成功响应**（200）：
```json
{
  "stats": {
    "total_submissions": 1000,
    "correct_submissions": 650,
    "accuracy_rate": 65.0,
    "user_total": 50,
    "user_correct": 32,
    "user_accuracy": 64.0,
    "recent_submissions": 150
  }
}
```

**示例**：
```bash
curl -X GET http://localhost:5000/api/v1/submissions/stats \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## 6. 管理员模块

### 6.1 获取系统统计（管理员）

**接口描述**：获取平台整体统计数据（仅管理员）

**请求方法**：GET

**接口路径**：`/admin/stats`

**请求头**：
```http
Authorization: Bearer L1BU0vHwj0NwS75duJ5EB1eiEGMw1GDj2FOOeI2hn46rfDAbvJB08qOBi0KgfqLg
```

**成功响应**（200）：
```json
{
  "stats": {
    "total_users": 150,
    "total_challenges": 50,
    "total_submissions": 1000,
    "recent_users": 15,
    "recent_submissions": 150,
    "user_growth": 30,
    "challenges_by_difficulty": [
      {"difficulty": "easy", "count": 15},
      {"difficulty": "medium", "count": 20},
      {"difficulty": "hard", "count": 10},
      {"difficulty": "expert", "count": 5}
    ]
  }
}
```

**示例**：
```bash
curl -X GET http://localhost:5000/api/v1/admin/stats \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 6.2 获取用户列表（管理员）

**接口描述**：获取所有用户列表（仅管理员）

**请求方法**：GET

**接口路径**：`/admin/users`

**请求头**：
```http
Authorization: Bearer L1BU0vHwj0NwS75duJ5EB1eiEGMw1GDj2FOOeI2hn46rfDAbvJB08qOBi0KgfqLg
```

**查询参数**：
| 参数名   | 类型    | 必填 | 说明             |
| -------- | ------- | ---- | ---------------- |
| page     | integer | 否   | 页码，默认1      |
| per_page | integer | 否   | 每页数量，默认20 |

**成功响应**（200）：
```json
{
  "users": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "is_admin": true,
      "score": 0,
      "created_at": "2025-10-15T08:30:00Z",
      "last_login": "2025-10-20T10:30:00Z"
    },
    {
      "id": 2,
      "username": "testuser",
      "email": "test@example.com",
      "is_admin": false,
      "score": 1200,
      "created_at": "2025-10-16T09:00:00Z",
      "last_login": "2025-10-19T14:20:00Z"
    }
  ],
  "total": 150,
  "pages": 8,
  "current_page": 1
}
```

**示例**：
```bash
curl -X GET "http://localhost:5000/api/v1/admin/users?page=1&per_page=20" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 6.3 更新用户信息（管理员）

**接口描述**：更新用户信息（仅管理员）

**请求方法**：PUT

**接口路径**：`/admin/users/{user_id}`

**路径参数**：
| 参数名  | 类型    | 必填 | 说明   |
| ------- | ------- | ---- | ------ |
| user_id | integer | 是   | 用户ID |

**请求头**：
```http
Authorization: Bearer L1BU0vHwj0NwS75duJ5EB1eiEGMw1GDj2FOOeI2hn46rfDAbvJB08qOBi0KgfqLg
Content-Type: application/json
```

**请求体**：
```json
{
  "username": "string, 用户名，可选",
  "email": "string, 邮箱，可选",
  "is_admin": "boolean, 管理员权限，可选",
  "score": "integer, 分数，可选"
}
```

**成功响应**（200）：
```json
{
  "message": "User updated successfully!"
}
```

**示例**：
```bash
curl -X PUT http://localhost:5000/api/v1/admin/users/2 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"is_admin": true, "score": 1500}'
```

### 6.4 删除用户（管理员）

**接口描述**：删除用户（仅管理员）

**请求方法**：DELETE

**接口路径**：`/admin/users/{user_id}`

**路径参数**：
| 参数名  | 类型    | 必填 | 说明   |
| ------- | ------- | ---- | ------ |
| user_id | integer | 是   | 用户ID |

**请求头**：
```http
Authorization: Bearer L1BU0vHwj0NwS75duJ5EB1eiEGMw1GDj2FOOeI2hn46rfDAbvJB08qOBi0KgfqLg
```

**成功响应**（200）：
```json
{
  "message": "User deleted successfully!"
}
```

**示例**：
```bash
curl -X DELETE http://localhost:5000/api/v1/admin/users/2 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 6.5 创建分类（管理员）

**接口描述**：创建新的题目分类（仅管理员）

**请求方法**：POST

**接口路径**：`/admin/categories`

**请求头**：
```http
Authorization: Bearer L1BU0vHwj0NwS75duJ5EB1eiEGMw1GDj2FOOeI2hn46rfDAbvJB08qOBi0KgfqLg
Content-Type: application/json
```

**请求体**：
```json
{
  "name": "string, 分类名称，必填",
  "description": "string, 分类描述，可选"
}
```

**成功响应**（201）：
```json
{
  "message": "Category created successfully!",
  "category_id": 6
}
```

**示例**：
```bash
curl -X POST http://localhost:5000/api/v1/admin/categories \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"name":"Forensics","description":"数字取证题目"}'
```

### 6.6 更新分类（管理员）

**接口描述**：更新题目分类信息（仅管理员）

**请求方法**：PUT

**接口路径**：`/admin/categories/{category_id}`

**路径参数**：
| 参数名      | 类型    | 必填 | 说明   |
| ----------- | ------- | ---- | ------ |
| category_id | integer | 是   | 分类ID |

**请求头**：
```http
Authorization: Bearer L1BU0vHwj0NwS75duJ5EB1eiEGMw1GDj2FOOeI2hn46rfDAbvJB08qOBi0KgfqLg
Content-Type: application/json
```

**请求体**：
```json
{
  "name": "string, 分类名称，可选",
  "description": "string, 分类描述，可选"
}
```

**成功响应**（200）：
```json
{
  "message": "Category updated successfully!"
}
```

**示例**：
```bash
curl -X PUT http://localhost:5000/api/v1/admin/categories/6 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"description":"数字取证和文件分析题目"}'
```

### 6.7 删除分类（管理员）

**接口描述**：删除题目分类（仅管理员）

**请求方法**：DELETE

**接口路径**：`/admin/categories/{category_id}`

**路径参数**：
| 参数名      | 类型    | 必填 | 说明   |
| ----------- | ------- | ---- | ------ |
| category_id | integer | 是   | 分类ID |

**请求头**：
```http
Authorization: Bearer L1BU0vHwj0NwS75duJ5EB1eiEGMw1GDj2FOOeI2hn46rfDAbvJB08qOBi0KgfqLg
```

**成功响应**（200）：
```json
{
  "message": "Category deleted successfully!"
}
```

**示例**：
```bash
curl -X DELETE http://localhost:5000/api/v1/admin/categories/6 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 6.8 获取所有提交记录（管理员）

**接口描述**：获取所有提交记录（仅管理员）

**请求方法**：GET

**接口路径**：`/admin/submissions`

**请求头**：
```http
Authorization: Bearer L1BU0vHwj0NwS75duJ5EB1eiEGMw1GDj2FOOeI2hn46rfDAbvJB08qOBi0KgfqLg
```

**查询参数**：
| 参数名   | 类型    | 必填 | 说明             |
| -------- | ------- | ---- | ---------------- |
| page     | integer | 否   | 页码，默认1      |
| per_page | integer | 否   | 每页数量，默认50 |

**成功响应**（200）：
```json
{
  "submissions": [
    {
      "id": 1,
      "user_id": 1,
      "username": "testuser",
      "challenge_id": 1,
      "challenge_title": "SQL注入挑战",
      "flag_submitted": "CTF{test_flag}",
      "is_correct": true,
      "submitted_at": "2025-10-15T10:30:00Z"
    }
  ],
  "total": 1000,
  "pages": 20,
  "current_page": 1
}
```

**示例**：
```bash
curl -X GET "http://localhost:5000/api/v1/admin/submissions?page=1&per_page=50" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 6.9 更新题目分数（管理员）

**接口描述**：更新所有题目的动态分数（仅管理员）

**请求方法**：POST

**接口路径**：`/admin/update-scores`

**请求头**：
```http
Authorization: Bearer L1BU0vHwj0NwS75duJ5EB1eiEGMw1GDj2FOOeI2hn46rfDAbvJB08qOBi0KgfqLg
```

**成功响应**（200）：
```json
{
  "message": "Scores updated successfully!"
}
```

**示例**：
```bash
curl -X POST http://localhost:5000/api/v1/admin/update-scores \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 6.10 导出平台数据（管理员）

**接口描述**：导出平台所有数据（仅管理员）

**请求方法**：GET

**接口路径**：`/admin/export-data`

**请求头**：
```http
Authorization: Bearer L1BU0vHwj0NwS75duJ5EB1eiEGMw1GDj2FOOeI2hn46rfDAbvJB08qOBi0KgfqLg
```

**成功响应**（200）：
```json
{
  "export_time": "2025-10-20T10:30:00Z",
  "users": [...],
  "challenges": [...],
  "submissions": [...],
  "categories": [...]
}
```

**示例**：
```bash
curl -X GET http://localhost:5000/api/v1/admin/export-data \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -o ctf_export_20251020.json
```

### 6.11 创建备份（管理员）

**接口描述**：创建系统备份（仅管理员）

**请求方法**：POST

**接口路径**：`/admin/backup`

**请求头**：
```http
Authorization: Bearer L1BU0vHwj0NwS75duJ5EB1eiEGMw1GDj2FOOeI2hn46rfDAbvJB08qOBi0KgfqLg
```

**成功响应**（200）：
```json
{
  "message": "Backup created successfully!",
  "backup": {
    "timestamp": "2025-10-20T10:30:00Z",
    "users_count": 150,
    "challenges_count": 50,
    "submissions_count": 1000
  }
}
```

**示例**：
```bash
curl -X POST http://localhost:5000/api/v1/admin/backup \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## 7. 系统接口

### 7.1 健康检查

**接口描述**：检查系统健康状态

**请求方法**：GET

**接口路径**：`/health`

**成功响应**（200）：
```json
{
  "status": "healthy",
  "timestamp": "2025-10-20T10:30:00Z",
  "database": "connected"
}
```

**示例**：
```bash
curl -X GET http://localhost:5000/health
```

### 7.2 根路径

**接口描述**：获取API基本信息

**请求方法**：GET

**接口路径**：`/`

**成功响应**（200）：
```json
{
  "message": "CTF Platform API",
  "version": "1.1",
  "timestamp": "2025-10-20T10:30:00Z"
}
```

**示例**：
```bash
curl -X GET http://localhost:5000/
```

## 8. 数据模型

### 8.1 用户模型
```json
{
  "id": "integer, 用户ID",
  "username": "string, 用户名",
  "email": "string, 邮箱地址",
  "is_admin": "boolean, 是否管理员",
  "score": "integer, 积分",
  "created_at": "string, 创建时间(ISO格式)",
  "last_login": "string, 最后登录时间(ISO格式)"
}
```

### 8.2 题目模型
```json
{
  "id": "integer, 题目ID",
  "title": "string, 标题",
  "description": "string, 描述",
  "category": "string, 分类名称",
  "category_id": "integer, 分类ID",
  "difficulty": "string, 难度(easy/medium/hard/expert)",
  "points": "integer, 分数",
  "solved_count": "integer, 解决人数",
  "is_solved": "boolean, 当前用户是否已解决",
  "is_hidden": "boolean, 是否隐藏",
  "created_at": "string, 创建时间(ISO格式)",
  "updated_at": "string, 更新时间(ISO格式)",
  "hints": ["string", "提示列表"],
  "attachment_filename": "string, 附件文件名",
  "attachment_url": "string, 附件下载URL"
}
```

### 8.3 分类模型
```json
{
  "id": "integer, 分类ID",
  "name": "string, 分类名称",
  "description": "string, 分类描述",
  "created_at": "string, 创建时间(ISO格式)"
}
```

### 8.4 提交记录模型
```json
{
  "id": "integer, 提交ID",
  "user_id": "integer, 用户ID",
  "username": "string, 用户名",
  "challenge_id": "integer, 题目ID",
  "challenge_title": "string, 题目标题",
  "flag_submitted": "string, 提交的Flag",
  "is_correct": "boolean, 是否正确",
  "submitted_at": "string, 提交时间(ISO格式)"
}
```

## 9. 错误码说明

### 9.1 通用错误码
| 错误码 | 说明         | 可能原因                       |
| ------ | ------------ | ------------------------------ |
| 1001   | 参数验证失败 | 请求参数格式错误或缺少必要参数 |
| 1002   | 资源不存在   | 请求的资源ID不存在             |
| 1003   | 权限不足     | 用户没有执行该操作的权限       |
| 1004   | 认证失败     | Token无效或已过期              |
| 1005   | 频率限制     | 请求过于频繁                   |
| 1006   | 系统错误     | 服务器内部错误                 |

### 9.2 业务错误码
| 错误码 | 说明         | 可能原因             |
| ------ | ------------ | -------------------- |
| 2001   | 用户名已存在 | 注册时用户名重复     |
| 2002   | 邮箱已存在   | 注册时邮箱重复       |
| 2003   | 题目已解决   | 重复提交已解决的题目 |
| 2004   | 题目不可见   | 题目被隐藏或不存在   |
| 2005   | Flag错误     | 提交的Flag不正确     |
| 2006   | 分类有题目   | 删除包含题目的分类   |

## 10. 使用示例

### 10.1 完整的用户流程示例

```bash
# 1. 注册新用户
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"newuser","email":"newuser@example.com","password":"password123"}'

# 2. 登录获取Token
TOKEN=$(curl -s -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"newuser","password":"password123"}' | jq -r '.token')

# 3. 获取题目列表
curl -X GET http://localhost:5000/api/v1/challenges \
  -H "Authorization: Bearer $TOKEN"

# 4. 获取题目详情
curl -X GET http://localhost:5000/api/v1/challenges/1 \
  -H "Authorization: Bearer $TOKEN"

# 5. 提交Flag
curl -X POST http://localhost:5000/api/v1/challenges/1/submit \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"flag":"CTF{test_flag}"}'

# 6. 查看排行榜
curl -X GET http://localhost:5000/api/v1/leaderboard \
  -H "Authorization: Bearer $TOKEN"

# 7. 查看提交记录
curl -X GET "http://localhost:5000/api/v1/submissions?page=1" \
  -H "Authorization: Bearer $TOKEN"
```

### 10.2 管理员操作示例

```bash
# 1. 管理员登录
ADMIN_TOKEN=$(curl -s -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.token')

# 2. 查看系统统计
curl -X GET http://localhost:5000/api/v1/admin/stats \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# 3. 创建新题目
curl -X POST http://localhost:5000/api/v1/challenges \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "新挑战",
    "description": "这是新的挑战",
    "flag": "CTF{new_challenge}",
    "points": 200,
    "difficulty": "medium",
    "category_id": 1,
    "hints": ["提示1", "提示2"],
    "is_hidden": false
  }'

# 4. 查看所有用户
curl -X GET "http://localhost:5000/api/v1/admin/users?page=1" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# 5. 导出数据
curl -X GET http://localhost:5000/api/v1/admin/export-data \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -o backup.json
```

## 11. 注意事项

### 11.1 安全注意事项
1. 所有敏感操作（登录、注册、提交Flag）都应使用HTTPS
2. Token应妥善保管，避免泄露
3. 管理员操作应使用强密码并定期更换
4. 定期检查日志，监控异常访问

### 11.2 性能注意事项
1. 排行榜查询可能在大数据量时较慢，建议定期优化
2. 文件上传应限制大小和类型
3. 数据库连接应使用连接池

### 11.3 开发注意事项
1. 所有API调用都应处理可能的错误响应
2. 前端应对Token过期进行自动处理
3. 重要操作应有确认提示

---

**文档维护**：林文进  
**最后更新**：2025年11月15日  
**版本**：1.1