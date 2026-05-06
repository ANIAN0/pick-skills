#!/usr/bin/env python3
"""
batch_generate.py - 批量生成HTML原型页面。

用法：
  python batch_generate.py --config pages.json

pages.json 格式：
{
  "output_path": ".dev/prototype",
  "pages": [
    {
      "page_name": "角色列表",
      "page_type": "list",
      "scenario": "new",
      "clarification": {...}
    },
    ...
  ]
}
"""

import argparse
import json
import os
import sys
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed


def generate_single_page(page_config, output_path, script_dir):
    """生成单个页面"""
    page_config['output_path'] = output_path
    input_json = json.dumps(page_config, ensure_ascii=False)

    script_path = os.path.join(script_dir, 'generate_page.py')
    try:
        result = subprocess.run(
            [sys.executable, script_path, '--input', input_json],
            capture_output=True, text=True, encoding='utf-8'
        )
        if result.returncode == 0:
            return {'page': page_config.get('page_name', ''), 'status': 'success', 'output': result.stdout}
        else:
            return {'page': page_config.get('page_name', ''), 'status': 'error', 'error': result.stderr}
    except Exception as e:
        return {'page': page_config.get('page_name', ''), 'status': 'error', 'error': str(e)}


def main():
    parser = argparse.ArgumentParser(description='批量生成HTML原型页面')
    parser.add_argument('--config', required=True, help='批量配置文件路径')
    parser.add_argument('--workers', type=int, default=3, help='并行工作线程数（默认3）')
    args = parser.parse_args()

    with open(args.config, 'r', encoding='utf-8') as f:
        config = json.load(f)

    output_path = config.get('output_path', '.dev/prototype')
    pages = config.get('pages', [])
    script_dir = os.path.dirname(os.path.abspath(__file__))

    os.makedirs(output_path, exist_ok=True)

    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(generate_single_page, page, output_path, script_dir): page
            for page in pages
        }
        for future in as_completed(futures):
            results.append(future.result())

    success_count = sum(1 for r in results if r['status'] == 'success')
    error_count = sum(1 for r in results if r['status'] == 'error')

    print(f'\n批量生成完成: {success_count} 成功, {error_count} 失败')
    for r in results:
        if r['status'] == 'success':
            print(f"  ✅ {r['page']}: {r['output'].strip()}")
        else:
            print(f"  ❌ {r['page']}: {r['error']}")

    # 输出结果汇总
    summary = {
        'total': len(pages),
        'success': success_count,
        'error': error_count,
        'results': results
    }

    summary_path = os.path.join(output_path, 'batch_summary.json')
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f'\n汇总已保存到: {summary_path}')


if __name__ == '__main__':
    main()
