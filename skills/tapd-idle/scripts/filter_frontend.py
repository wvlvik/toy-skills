"""
Filter frontend group tasks from TAPD API response.

Usage:
    # First fetch workspace users and tasks, then pipe to this script
    { python scripts/tapd.py get_workspace_users --workspace_id 50372234
      sleep 1
      python scripts/tapd.py get_stories_or_tasks --workspace_id 50372234 --entity_type tasks --fields "id,name,owner,status,begin,due,effort,remain" --limit 500
    } | python scripts/filter_frontend.py [--today 2026-04-08]

This script dynamically extracts frontend group members by role_id (1150372234001000020)
instead of using hardcoded member names.
"""
import argparse
import json
import sys

# 前端组 role_id
FRONTEND_ROLE_ID = "1150372234001000020"


def parse_args():
    parser = argparse.ArgumentParser(description="Filter frontend group tasks")
    parser.add_argument("--today", default=None, help="Today's date (YYYY-MM-DD)")
    return parser.parse_args()


def main():
    args = parse_args()

    # 读取所有 JSON 输入
    all_json = []
    for line in sys.stdin:
        line = line.strip()
        if line and line.startswith("{"):
            try:
                all_json.append(json.loads(line))
            except json.JSONDecodeError:
                pass

    if not all_json:
        print("No JSON found", file=sys.stderr)
        sys.exit(1)

    # 动态提取前端组成员（通过 role_id）
    frontend_members = set()
    for data in all_json:
        if data.get("status") == 1:
            for item in data.get("data", []):
                user = item.get("UserWorkspace", {})
                if FRONTEND_ROLE_ID in user.get("role_id", []):
                    name = user.get("name") or user.get("user")
                    if name:
                        frontend_members.add(name)

    if not frontend_members:
        print("Warning: No frontend members found via role_id", file=sys.stderr)

    # 按成员分组任务
    tasks_by_member = {}
    for member in frontend_members:
        tasks_by_member[member] = {
            "progressing": [],
            "open_today": [],
            "done_today": [],
        }

    for data in all_json:
        for item in data.get("data", []):
            task = item.get("Task")
            if not task:
                continue

            owner = task.get("owner", "").rstrip(";")
            status = task.get("status", "")
            begin = task.get("begin", "")
            due = task.get("due", "")
            name = task.get("name", "")
            task_id = task.get("id", "")
            effort = task.get("effort", "0") or "0"
            remain = task.get("remain", "0") or "0"

            # 只处理前端组成员
            if owner not in frontend_members:
                continue

            # 确保成员在字典中
            if owner not in tasks_by_member:
                tasks_by_member[owner] = {
                    "progressing": [],
                    "open_today": [],
                    "done_today": [],
                }

            task_info = {
                "id": task_id,
                "name": name,
                "begin": begin,
                "due": due,
                "effort": effort,
                "remain": remain,
            }

            if status == "progressing":
                tasks_by_member[owner]["progressing"].append(task_info)
            elif args.today:
                is_today = begin == args.today or due == args.today
                if status == "open" and is_today:
                    tasks_by_member[owner]["open_today"].append(task_info)
                elif status == "done" and is_today:
                    tasks_by_member[owner]["done_today"].append(task_info)

    print(json.dumps(tasks_by_member, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
