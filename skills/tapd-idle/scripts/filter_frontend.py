import json
import sys

# 前端组成员
frontend_members = ['陈方杰', '文武', '吴铝', '刘子昱', '唐尧', '戴婕妤', '李金涛', '熊思', '曹振辉', '陈铁梁', '方乐', '汤显文', '周树梧', '刘奕君']

# 今日日期
today = '2026-04-08'

# 读取 stdin
raw = sys.stdin.read()
# 去掉 urllib3 warning
lines = raw.strip().split('\n')
json_line = None
for line in lines:
    if line.startswith('{'):
        json_line = line
        break

if not json_line:
    print("No JSON found")
    sys.exit(1)

data = json.loads(json_line)

# 筛选前端组成员的今日相关任务
tasks_by_member = {}
for member in frontend_members:
    tasks_by_member[member] = {
        'progressing': [],
        'open_today': [],
        'done_today': [],
        'other': []
    }

for item in data['data']:
    task = item['Task']
    owner = task.get('owner', '').rstrip(';')
    status = task.get('status', '')
    begin = task.get('begin', '')
    due = task.get('due', '')
    name = task.get('name', '')
    id = task.get('id', '')
    effort = task.get('effort', '0') or '0'
    remain = task.get('remain', '0') or '0'
    
    # 检查是否是前端组成员
    if owner not in frontend_members:
        continue
    
    # 筛选今日相关任务
    is_today = (begin == today or due == today)
    
    if status == 'progressing':
        tasks_by_member[owner]['progressing'].append({
            'id': id, 'name': name, 'begin': begin, 'due': due, 'effort': effort, 'remain': remain
        })
    elif status == 'open' and is_today:
        tasks_by_member[owner]['open_today'].append({
            'id': id, 'name': name, 'begin': begin, 'due': due, 'effort': effort, 'remain': remain
        })
    elif status == 'done' and is_today:
        tasks_by_member[owner]['done_today'].append({
            'id': id, 'name': name, 'begin': begin, 'due': due, 'effort': effort, 'remain': remain
        })

# 输出结果
print(json.dumps(tasks_by_member, ensure_ascii=False, indent=2))