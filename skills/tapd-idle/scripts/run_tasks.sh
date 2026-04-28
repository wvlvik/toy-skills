#!/bin/bash
cd /Users/lv/.openclaw/workspace/skills/tapd-idle/scripts
python3 tapd.py get_stories_or_tasks --workspace_id 50372234 --entity_type tasks --fields "id,name,owner,status,begin,due,effort,effort_completed,remain" --limit 300
