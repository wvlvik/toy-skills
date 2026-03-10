---
name: tapd-idle
description: (project - Skill) TAPD 敏捷研发管理平台集成（项目本地版本）。使用脚本调用 TAPD API，实现需求、缺陷、任务、迭代、测试用例、Wiki 等实体管理。使用场景包括：(1) 查询/创建/更新需求、缺陷、任务、迭代 (2) 管理测试用例和 Wiki (3) 管理评论和工时 (4) 关联需求与缺陷 (5) 获取源码提交关键字 (6) 查询用户组和项目成员。Triggers: "TAPD", "需求", "缺陷", "迭代", "工时", "看板", "敏捷"
---

# TAPD Skill

TAPD 敏捷研发管理平台集成，通过 Python 脚本调用 TAPD API。

## Agent 使用指南

### 何时使用此 Skill

当用户需要与 TAPD 平台交互时，主动调用此 skill：

**触发关键词**：
- TAPD、看板、敏捷、需求管理
- 查询/创建/更新 需求、缺陷、任务、迭代
- 工时填写、评论管理
- 测试用例、Wiki 管理

### Agent 工作流程

1. **理解用户意图** → 确定 TAPD 操作类型
2. **构建命令** → 使用 `python scripts/tapd.py <command> [参数]`
3. **执行脚本** → 使用 Bash 工具运行
4. **处理结果** → 解析 JSON 输出，向用户报告

### 示例对话

```
用户: "查看需求 1167459320001114969 的详情"

Agent:
1. 识别操作：查询需求详情
2. 执行: python scripts/tapd.py get_stories_or_tasks --workspace_id 67459320 --entity_type stories --id 1167459320001114969
3. 解析返回的需求信息并向用户报告
```

## 环境配置

使用前需要配置以下环境变量：

```bash
export TAPD_ACCESS_TOKEN="你的个人访问令牌"  # 推荐
# 或
export TAPD_API_USER="API账号"
export TAPD_API_PASSWORD="API密钥"

export TAPD_API_BASE_URL="https://api.tapd.cn"  # 可选，默认
export TAPD_BASE_URL="https://www.tapd.cn"      # 可选，默认
export CURRENT_USER_NICK="你的昵称"               # 可选
```

## 常用项目 ID

| 项目名称 | workspace_id |
|----------|--------------|
| 聚宝赞 | 50372234 |

## 命令速查表

### 项目与用户

| 命令 | 说明 |
|------|------|
| `get_user_participant_projects` | 获取用户参与的项目列表 |
| `get_workspace_info` | 获取项目信息 |
| `get_workitem_types` | 获取需求类别 |
| `get_roles` | 获取用户组ID对照关系 |
| `get_workspace_users` | 获取项目成员列表 |
| `get_group_members` | 获取指定用户组的成员 |

### 需求/任务

| 命令 | 说明 |
|------|------|
| `get_stories_or_tasks` | 查询需求/任务 |
| `create_story_or_task` | 创建需求/任务 |
| `update_story_or_task` | 更新需求/任务 |
| `get_story_or_task_count` | 获取数量 |
| `get_stories_fields_lable` | 字段中英文对照 |
| `get_stories_fields_info` | 字段及候选值 |

### 缺陷

| 命令 | 说明 |
|------|------|
| `get_bug` | 查询缺陷 |
| `create_bug` | 创建缺陷 |
| `update_bug` | 更新缺陷 |
| `get_bug_count` | 获取数量 |

### 迭代

| 命令 | 说明 |
|------|------|
| `get_iterations` | 查询迭代 |
| `create_iteration` | 创建迭代 |
| `update_iteration` | 更新迭代 |

### 评论

| 命令 | 说明 |
|------|------|
| `get_comments` | 查询评论 |
| `create_comments` | 创建评论 |
| `update_comments` | 更新评论 |

### 工时

| 命令 | 说明 |
|------|------|
| `get_timesheets` | 查询工时 |
| `add_timesheets` | 填写工时 |
| `update_timesheets` | 更新工时 |

### 其他命令

| 分类 | 命令 |
|------|------|
| 附件 | `get_entity_attachments`, `get_image` |
| 自定义字段 | `get_entity_custom_fields` |
| 工作流 | `get_workflows_status_map`, `get_workflows_all_transitions`, `get_workflows_last_steps` |
| 测试用例 | `get_tcases`, `create_or_update_tcases`, `create_tcases_batch` |
| Wiki | `get_wiki`, `create_wiki`, `update_wiki` |
| 关联 | `get_related_bugs`, `entity_relations` |
| 源码 | `get_commit_msg` |
| 消息 | `send_qiwei_message` |

## 使用方式

```bash
python scripts/tapd.py <command> [参数]
```

所有命令默认输出 JSON 格式结果。

## 使用示例

### 查询需求

```bash
# 查询指定需求
python scripts/tapd.py get_stories_or_tasks --workspace_id 123 --entity_type stories --id 1167459320001114969

# 模糊搜索需求
python scripts/tapd.py get_stories_or_tasks --workspace_id 123 --entity_type stories --name "%登录%" --limit 20

# 查询指定状态的需求
python scripts/tapd.py get_stories_or_tasks --workspace_id 123 --entity_type stories --v_status "已验收"
```

### 创建需求

```bash
python scripts/tapd.py create_story_or_task --workspace_id 123 \
    --name "用户登录功能" \
    --description "## 需求描述\n用户可以通过账号密码登录系统" \
    --priority_label "高" \
    --owner "zhangsan" \
    --iteration_name "Sprint 1"
```

### 更新需求状态

```bash
python scripts/tapd.py update_story_or_task --workspace_id 123 \
    --id 1167459320001114969 \
    --v_status "实现中"
```

### 查询缺陷

```bash
python scripts/tapd.py get_bug --workspace_id 123 --title "%登录失败%" --priority_label "高"
```

### 缺陷查询参数说明

> **重要**: TAPD API 参数与脚本参数对应关系：
> - `--owner` → API 参数 `current_owner`（处理人）
> - `--developer` → API 参数 `de`（开发人员）

| 脚本参数 | API 参数 | 说明 |
|---------|---------|------|
| `--owner` | `current_owner` | 处理人 |
| `--developer` | `de` | 开发人员 |
| `--created` | `created` | 创建时间范围 |
| `--version_report` | `version_report` | 发现版本 |
| `--closed` | `status` | 结束状态别名（closed\|rejected\|suspended） |
| `--open` | `status` | 未结束状态别名（unconfirmed\|in_progress\|resolved\|verified） |
| `--exclude_status` | - | 排除指定状态（结果过滤） |

### 缺陷状态说明

| 英文状态 | 中文状态 | 类型 |
|---------|---------|------|
| `unconfirmed` | 缺陷池 | 未结束 |
| `in_progress` | 修复中 | 未结束 |
| `resolved` | 待测试 | 未结束 |
| `verified` | 测试中 | 未结束 |
| `closed` | 完成 | **结束** |
| `rejected` | 拒绝 | **结束** |
| `suspended` | 关闭 | **结束** |

### 缺陷查询示例

**按开发人员过滤**：使用 `--developer` 参数
```bash
# 按开发人员查询缺陷
python scripts/tapd.py get_bug --workspace_id 50372234 --developer "张三"
```

**按处理人过滤**：使用 `--owner` 参数
```bash
# 按处理人查询缺陷
python scripts/tapd.py get_bug --workspace_id 50372234 --owner "张三"
```

**按状态别名查询**：使用 `--closed` 或 `--open` 参数
```bash
# 查询结束状态的缺陷（closed|rejected|suspended）
python scripts/tapd.py get_bug --workspace_id 50372234 --closed --developer "陈方杰"

# 查询未结束状态的缺陷（unconfirmed|in_progress|resolved|verified）
python scripts/tapd.py get_bug --workspace_id 50372234 --open --developer "陈方杰"
```

**排除指定状态**：使用 `--exclude_status` 参数
```bash
# 查询全部状态，排除完成和挂起
python scripts/tapd.py get_bug --workspace_id 50372234 --exclude_status "closed|suspended" --developer "陈方杰"
```

**按时间范围查询**：
```bash
python scripts/tapd.py get_bug --workspace_id 50372234 \
    --created "2026-02-01~2026-02-28"
```

**按发现版本查询**：
```bash
# 查询线上版本缺陷
python scripts/tapd.py get_bug --workspace_id 50372234 \
    --version_report "线上版本"

# 查询测试版本缺陷
python scripts/tapd.py get_bug --workspace_id 50372234 \
    --version_report "测试版本"
```

### 人员缺陷统计

**查询某人某月的所有缺陷**：
```bash
python scripts/tapd.py get_bug --workspace_id 50372234 \
    --developer "姓名" \
    --created "2026-02-01~2026-02-28" \
    --fields "id,title,severity,status,version_report,created"
```

**统计某人缺陷数量**：
```bash
python scripts/tapd.py get_bug_count --workspace_id 50372234 \
    --developer "姓名" \
    --created "2026-02-01~2026-02-28"
```

**区分线上/测试缺陷**：
```bash
# 线上缺陷（生产质量）
python scripts/tapd.py get_bug_count --workspace_id 50372234 \
    --developer "姓名" \
    --version_report "线上版本" \
    --created "2026-02-01~2026-02-28"

# 测试缺陷（测试质量）
python scripts/tapd.py get_bug_count --workspace_id 50372234 \
    --developer "姓名" \
    --version_report "测试版本" \
    --created "2026-02-01~2026-02-28"
```

### 创建缺陷

```bash
python scripts/tapd.py create_bug --workspace_id 123 \
    --title "登录页面显示异常" \
    --description "输入正确密码后提示错误" \
    --priority_label "高" \
    --severity "严重"
```

### 迭代管理

```bash
# 查询迭代
python scripts/tapd.py get_iterations --workspace_id 123

# 创建迭代
python scripts/tapd.py create_iteration --workspace_id 123 \
    --name "Sprint 1" \
    --startdate "2024-01-01" \
    --enddate "2024-01-14" \
    --creator "zhangsan"
```

### 工时管理

```bash
# 查询工时
python scripts/tapd.py get_timesheets --workspace_id 123 --entity_type story --entity_id 1167459320001114969

# 填写工时
python scripts/tapd.py add_timesheets --workspace_id 123 \
    --entity_type story \
    --entity_id 1167459320001114969 \
    --timespent "4" \
    --spentdate "2024-01-08" \
    --memo "开发登录功能"
```

### 评论管理

```bash
# 查询评论
python scripts/tapd.py get_comments --workspace_id 123 \
    --entry_type stories \
    --entry_id 1167459320001114969

# 创建评论
python scripts/tapd.py create_comments --workspace_id 123 \
    --entry_type stories \
    --entry_id 1167459320001114969 \
    --description "看起来不错，可以继续完善"
```

### 用户组与成员

```bash
# 获取用户组ID对照关系
python scripts/tapd.py get_roles --workspace_id 123

# 获取项目成员列表
python scripts/tapd.py get_workspace_users --workspace_id 123

# 获取指定用户组的成员（如：前端开发组）
python scripts/tapd.py get_group_members --workspace_id 123 --group_name "前端开发"
```

## 常用命令速查

```bash
# 需求
python scripts/tapd.py get_stories_or_tasks --workspace_id $WS_ID --entity_type stories
python scripts/tapd.py create_story_or_task --workspace_id $WS_ID --name "标题"
python scripts/tapd.py update_story_or_task --workspace_id $WS_ID --id $ID --v_status "状态"

# 缺陷
python scripts/tapd.py get_bug --workspace_id $WS_ID
python scripts/tapd.py create_bug --workspace_id $WS_ID --title "标题"

# 迭代
python scripts/tapd.py get_iterations --workspace_id $WS_ID
python scripts/tapd.py create_iteration --workspace_id $WS_ID --name "Sprint X" --startdate "2024-01-01" --enddate "2024-01-14"

# 工时
python scripts/tapd.py add_timesheets --workspace_id $WS_ID --entity_type story --entity_id $ID --timespent 4 --spentdate "2024-01-08"

# 评论
python scripts/tapd.py create_comments --workspace_id $WS_ID --entry_type stories --entry_id $ID --description "评论内容"
```

## 状态值说明

| 类型 | 字段 | 可用值 |
|------|------|--------|
| 需求优先级 | `priority_label` | High / Middle / Low / Nice To Have |
| 缺陷优先级 | `priority_label` | urgent / high / medium / low / insignificant |
| 缺陷严重程度 | `severity` | fatal / serious / normal / prompt / advice |
| 任务状态 | `status` | open / progressing / done |
| 迭代状态 | `status` | open / done |

## 图片处理

当获取需求详情时，`get_stories_or_tasks` 命令会自动解析 description 中的图片并获取下载链接。

**返回结果包含 `images` 字段**：
```json
{
  "data": [
    {
      "Story": { "id": "1167459320001114969", "name": "需求标题", ... },
      "images": [
        {
          "path": "/tfl/captures/2026-01/tapd_67459320_base64_1767668922_121.png",
          "download_url": "https://file.tapd.cn/attachments/tmp_download/...?salt=...&time=...",
          "filename": "tapd_67459320_base64_1767668922_121.png"
        }
      ]
    }
  ]
}
```

**处理步骤**：
1. 从返回结果中读取 `images` 数组
2. 使用 `download_url` 访问或下载图片
3. 图片链接有效期约 300 秒

**手动获取图片**（备用方式）：
```bash
python scripts/tapd.py get_image --workspace_id 67459320 --image_path "/tfl/captures/2026-01/tapd_xxx.png"
```

## 文件结构

```
scripts/
├── tapd.py           # 统一入口脚本（46个子命令）
├── tapd_client.py    # TAPD API 客户端
└── requirements.txt
```

## 参考文档

详细的 API 使用说明请参阅 `references/` 目录：
- `stories-tasks.md` - 需求/任务操作指南
- `bugs.md` - 缺陷操作指南
- `iterations.md` - 迭代操作指南
- `fields.md` - 字段配置指南
- `testcases.md` - 测试用例操作指南
