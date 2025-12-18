# CTF平台贡献指南

感谢您对CTF平台项目的关注！本文档将指导您如何为项目做出贡献。

# CTF平台贡献指南

感谢您对CTF平台项目的关注！本文档将指导您如何为项目做出贡献。

## 开发团队

- **项目经理**: 林哲凯
- **前端工程师**: 卢圣轩
- **后端工程师**: 林文进
- **测试工程师**: 宋礼雄
- **运维工程师**: 杨鹏祥
- **渗透工程师**: 刘城铭

## 开发工作流

我们采用 **Git Flow** 工作流，主要分支如下：

- `main`: 主分支，用于生产环境部署
- `develop`: 开发分支，所有新特性都合并到此分支
- `feature/*`: 功能分支，用于开发新特性
- `release/*`: 发布分支，用于版本发布准备
- `hotfix/*`: 热修复分支，用于紧急修复
- `bugfix/*`: 缺陷修复分支

## 分支命名规范

分支名称应采用以下格式：

```
<类型>/<简短描述>
```

**类型说明：**

- `feat/`: 新功能（例如：`feat/user-profile-page`）
- `fix/`: bug修复（例如：`fix/login-validation`）
- `refactor/`: 代码重构（例如：`refactor/auth-module`）
- `docs/`: 文档更新（例如：`docs/api-documentation`）
- `test/`: 测试相关（例如：`test/user-authentication`）
- `perf/`: 性能优化（例如：`perf/query-optimization`）
- `chore/`: 构建过程或辅助工具的变动（例如：`chore/update-dependencies`）
- `security/`: 安全相关修改（例如：`security/sql-injection-fix`）

## Pull Request 流程

### 创建PR步骤

1. Fork 项目仓库
2. 创建功能分支：`git checkout -b feat/your-feature-name`
3. 提交更改：`git commit -m "描述你的更改"`
4. 推送到远程仓库：`git push origin feat/your-feature-name`
5. 在GitHub上创建Pull Request

### PR模板要求

创建Pull Request时，请包含以下信息：

- **标题格式：** `[类型] 简短描述`（例如：`[FEAT] 添加用户个人中心页面`）
- **描述内容：**
- 
- **关联的Issue**：`Closes #123` 或 `Related to #123`
- **变更描述**：
  - 这个PR做了什么？
  - 为什么要做这个变更？
- **测试情况**：
  - 本地测试结果
  - 单元测试/集成测试覆盖情况
  - 测试工程师：宋礼雄（已审核）

- **安全检查**：
  - 渗透测试结果：刘城铭（已审核）
  - 是否存在安全风险？

### 代码审查要求

1. **前端代码**需要卢圣轩审查
2. **后端代码**需要林文进审查
3. **安全性**需要刘城铭审查
4. **测试覆盖**需要宋礼雄验证
5. **最终合并**需要林哲凯批准

## 代码规范

### 前端规范（JavaScript）

- 使用ES6+语法
- 使用单引号
- 2个空格缩进
- 行尾分号
- 变量使用camelCase，常量使用UPPER_CASE
- 组件使用PascalCase

### 后端规范（Python）

- 遵循PEP 8规范
- 使用4个空格缩进
- 导入按标准库、第三方库、本地模块分组
- 函数和变量使用snake_case
- 类名使用PascalCase

### 数据库规范

- 表名使用复数形式（例如：`users`, `challenges`）
- 列名使用snake_case
- 外键命名：`<表名单数>_id`
- 索引命名：`idx_<表名>_<列名>`

## 提交信息规范

使用约定式提交（Conventional Commits）：

```
<类型>(<作用域>): <描述>

[可选正文]

[可选脚注]
```

**类型：**

- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档变更
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具变更

**示例：**

```
feat(auth): 添加用户邮箱验证功能

- 实现邮件发送功能
- 添加邮箱验证接口
- 更新用户注册流程

Closes #45
```

## 测试要求

1. 新功能必须包含单元测试
2. API接口必须包含集成测试
3. 前端组件需要E2E测试
4. 所有测试必须通过
5. 测试覆盖率不低于80%
