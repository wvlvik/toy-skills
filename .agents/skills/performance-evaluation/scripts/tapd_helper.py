#!/usr/bin/env python3
"""
TAPD 查询辅助脚本

功能：
1. 查询缺陷数据
2. 生成TAPD URL
3. 统计缺陷数量

用法：
    python3 tapd_helper.py query-bugs --developer "姓名" --version "线上版本" --created "2026-02-01~2026-02-28"
    python3 tapd_helper.py build-url --developer "姓名" --version "线上版本" --created "2026-02-01~2026-02-28"
    python3 tapd_helper.py count-bugs --developer "姓名" --version "线上版本" --created "2026-02-01~2026-02-28"
"""

import sys
import os
import argparse
import json

# 添加 tapd-idle scripts 目录到路径
script_dir = os.path.dirname(os.path.abspath(__file__))
# script_dir = .../performance-evaluation/scripts
# skills_dir = .../skills
skills_dir = os.path.dirname(os.path.dirname(script_dir))
tapd_scripts = os.path.join(skills_dir, 'tapd-idle', 'scripts')
sys.path.insert(0, tapd_scripts)

try:
    from tapd_client import TAPDClient
except ImportError:
    print("错误: 无法导入 TAPDClient")
    print("请确保 tapd-idle 技能已安装")
    sys.exit(1)

# 配置
WORKSPACE_ID = os.getenv('TAPD_WORKSPACE_ID', '50372234')  # 聚宝赞项目
TAPD_BASE_URL = 'https://www.tapd.cn'


def build_tapd_url(developer: str, version_report: str, created_range: str) -> str:
    """构建TAPD缺陷查询URL

    注意：TAPD前端URL使用 queryToken 机制，需要通过浏览器操作保存筛选条件后生成。
    这里返回的是缺陷列表基础URL，附带筛选条件作为URL锚点供参考。
    用户需要在前端手动设置过滤条件，或使用"保存筛选"功能生成可分享的链接。
    """
    # TAPD前端缺陷列表基础URL
    base_url = f"{TAPD_BASE_URL}/tapd_fe/{WORKSPACE_ID}/bug/list"

    # 构建筛选条件字符串（用于提示用户）
    filters = []
    if developer:
        filters.append(f"开发人员=\"{developer}\"")
    if version_report:
        filters.append(f"发现版本=\"{version_report}\"")
    if created_range:
        filters.append(f"创建时间=\"{created_range}\"")

    filter_note = " | ".join(filters) if filters else ""

    # 返回基础URL和筛选条件说明
    # 实际使用时需要用户在前端手动设置筛选条件
    return base_url


def query_bugs(developer: str, version_report: str, created_range: str, fields: str = None) -> dict:
    """查询TAPD缺陷"""
    client = TAPDClient()

    params = {
        'workspace_id': WORKSPACE_ID,
        'de': developer,  # API参数: de = 开发人员
        'version_report': version_report,
        'created': created_range,
        'limit': 100
    }

    if fields:
        params['fields'] = fields
    else:
        params['fields'] = 'id,title,developer,version_report,created,status,severity'

    result = client.get_bug(params)

    # 同时获取数量
    count_result = client.get_bug_count(params)
    count = count_result.get('data', {}).get('count', 0)

    # 构建筛选条件说明
    filter_conditions = []
    if developer:
        filter_conditions.append(f"开发人员=\"{developer}\"")
    if version_report:
        filter_conditions.append(f"发现版本=\"{version_report}\"")
    if created_range:
        filter_conditions.append(f"创建时间=\"{created_range}\"")
    filter_note = " | ".join(filter_conditions) if filter_conditions else ""

    return {
        'count': count,
        'bugs': result.get('data', []),
        'url': build_tapd_url(developer, version_report, created_range),
        'filter_note': filter_note  # 筛选条件说明
    }


def count_bugs(developer: str, version_report: str, created_range: str) -> int:
    """统计缺陷数量"""
    client = TAPDClient()

    params = {
        'workspace_id': WORKSPACE_ID,
        'de': developer,  # API参数: de = 开发人员
        'version_report': version_report,
        'created': created_range
    }

    result = client.get_bug_count(params)
    return result.get('data', {}).get('count', 0)


def main():
    parser = argparse.ArgumentParser(description='TAPD查询辅助脚本')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # query-bugs 命令
    query_parser = subparsers.add_parser('query-bugs', help='查询缺陷')
    query_parser.add_argument('--developer', required=True, help='开发人员姓名')
    query_parser.add_argument('--version', required=True, help='发现版本（线上版本/测试版本）')
    query_parser.add_argument('--created', required=True, help='创建时间范围（如 2026-02-01~2026-02-28）')
    query_parser.add_argument('--fields', help='返回字段（逗号分隔）')
    query_parser.add_argument('--json', action='store_true', help='输出JSON格式')

    # build-url 命令
    url_parser = subparsers.add_parser('build-url', help='生成TAPD URL')
    url_parser.add_argument('--developer', required=True, help='开发人员姓名')
    url_parser.add_argument('--version', required=True, help='发现版本')
    url_parser.add_argument('--created', required=True, help='创建时间范围')

    # count-bugs 命令
    count_parser = subparsers.add_parser('count-bugs', help='统计缺陷数量')
    count_parser.add_argument('--developer', required=True, help='开发人员姓名')
    count_parser.add_argument('--version', required=True, help='发现版本')
    count_parser.add_argument('--created', required=True, help='创建时间范围')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == 'query-bugs':
            result = query_bugs(args.developer, args.version, args.created, args.fields)

            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(f"缺陷数量: {result['count']}")
                print(f"TAPD URL: {result['url']}")
                print(f"\n缺陷列表:")
                for bug in result['bugs']:
                    bug_data = bug.get('Bug', bug)
                    print(f"  - {bug_data.get('id')}: {bug_data.get('title')}")

        elif args.command == 'build-url':
            url = build_tapd_url(args.developer, args.version, args.created)
            print(url)

        elif args.command == 'count-bugs':
            count = count_bugs(args.developer, args.version, args.created)
            print(count)

    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()