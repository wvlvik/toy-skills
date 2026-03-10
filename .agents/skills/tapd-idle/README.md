# TAPD Skill

TAPD 敏捷研发管理平台集成，通过 Python 脚本调用 TAPD API。

## 功能特性

- 需求/任务管理：查询、创建、更新需求与任务
- 缺陷管理：查询、创建、更新缺陷
- 迭代管理：查询、创建、更新迭代
- 工时管理：查询、填写、更新工时
- 评论管理：查询、创建、更新评论
- 测试用例：查询、创建、更新测试用例
- Wiki 管理：查询、创建、更新 Wiki
- 用户管理：查询项目成员、用户组

## 环境配置

### 必需环境变量

```bash
# 推荐：使用个人访问令牌
export TAPD_ACCESS_TOKEN="你的个人访问令牌"

# 或使用 API 账号
export TAPD_API_USER="API账号"
export TAPD_API_PASSWORD="API密钥"
```

### 可选环境变量

```bash
export TAPD_API_BASE_URL="https://api.tapd.cn"  # API 端点
export TAPD_BASE_URL="https://www.tapd.cn"      # Web 地址
export CURRENT_USER_NICK="你的昵称"               # 用户昵称
```

## 使用方式

```bash
python scripts/tapd.py <command> [参数]
```

### 常用命令

```bash
# 查询需求
python scripts/tapd.py get_stories_or_tasks --workspace_id 123 --entity_type stories

# 创建需求
python scripts/tapd.py create_story_or_task --workspace_id 123 --name "需求标题"

# 查询缺陷
python scripts/tapd.py get_bug --workspace_id 123

# 查询迭代
python scripts/tapd.py get_iterations --workspace_id 123

# 填写工时
python scripts/tapd.py add_timesheets --workspace_id 123 --entity_type story --entity_id 456 --timespent 4 --spentdate "2024-01-08"
```

## 依赖安装

```bash
pip install -r scripts/requirements.txt
```

## 文件结构

```
tapd-idle/
├── .antigravityrules     # Antigravity 规则
├── .cursorrules          # Cursor 规则
├── .opencode-rules       # OpenCode 规则
├── SKILL.md              # 主指令文件
├── package.json          # 包配置
├── README.md             # 说明文档
├── scripts/
│   ├── tapd.py           # 主入口脚本（46个子命令）
│   ├── tapd_client.py    # TAPD API 客户端
│   └── requirements.txt  # Python 依赖
└── references/           # 参考文档
    ├── stories-tasks.md  # 需求/任务指南
    ├── bugs.md           # 缺陷指南
    ├── iterations.md     # 迭代指南
    ├── fields.md         # 字段配置
    └── testcases.md      # 测试用例指南
```

## 支持的智能体

- OpenCode
- Cursor
- Antigravity
- Claude Code
- Windsurf

## 许可证

MIT