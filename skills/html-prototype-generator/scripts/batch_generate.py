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
from datetime import datetime
from pathlib import Path


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


def generate_index_html(output_path, pages_info):
    """生成 index.html 目录页"""
    type_order = {'list': 0, 'form': 1, 'detail': 2, 'dashboard': 3}
    type_labels = {'list': 'list', 'form': 'form', 'detail': 'detail', 'dashboard': 'dashboard'}
    type_css = {'list': 'type-list', 'form': 'type-form', 'detail': 'type-detail', 'dashboard': 'type-dashboard'}

    sorted_pages = sorted(pages_info, key=lambda p: (type_order.get(p.get('page_type', 'list'), 99), p.get('page_name', '')))

    cards_html = ''
    for page in sorted_pages:
        file_name = page.get('file_name', '')
        page_name = page.get('page_name', '')
        page_type = page.get('page_type', 'list')
        description = page.get('description', '')
        type_css_class = type_css.get(page_type, 'type-list')
        type_label = type_labels.get(page_type, page_type)

        cards_html += f'''
    <div class="index-card">
      <a href="{file_name}" target="_blank">
        {page_name}
        <span class="page-type-tag {type_css_class}">{type_label}</span>
      </a>
      <div class="meta">{description}</div>
    </div>'''

    date_str = datetime.now().strftime('%Y-%m-%d')
    total = len(sorted_pages)

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>原型目录</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/antd/4.24.15/antd.min.css">
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body {{ background: #f0f2f5; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
    .index-card {{ background: #fff; border-radius: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.04); padding: 20px 24px; margin-bottom: 16px; transition: box-shadow 0.2s; }}
    .index-card:hover {{ box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
    .index-card a {{ color: #3e8dff; text-decoration: none; font-size: 16px; font-weight: 500; }}
    .index-card a:hover {{ color: #5ea3ff; }}
    .page-type-tag {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-left: 8px; }}
    .type-list {{ background: #e6f7ff; color: #1890ff; }}
    .type-form {{ background: #f6ffed; color: #52c41a; }}
    .type-detail {{ background: #fff7e6; color: #fa8c16; }}
    .type-dashboard {{ background: #f9f0ff; color: #722ed1; }}
    .meta {{ color: rgba(0,0,0,0.45); font-size: 13px; margin-top: 8px; }}
  </style>
</head>
<body>
  <div style="max-width: 800px; margin: 0 auto; padding: 40px 24px;">
    <h1 style="font-size: 24px; font-weight: 600; color: rgba(0,0,0,0.85); margin-bottom: 8px;">原型页面目录</h1>
    <p style="color: rgba(0,0,0,0.45); font-size: 14px; margin-bottom: 32px;">生成日期：{date_str} | 共 {total} 个页面</p>
{cards_html}
  </div>
</body>
</html>'''

    index_path = os.path.join(output_path, 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)
    return index_path


def main():
    parser = argparse.ArgumentParser(description='批量生成HTML原型页面')
    parser.add_argument('--config', required=True, help='批量配置文件路径')
    parser.add_argument('--workers', type=int, default=3, help='并行工作线程数（默认3）')
    parser.add_argument('--skip-index', action='store_true', help='跳过生成 index.html 目录页')
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
            print(f"  [OK] {r['page']}: {r['output'].strip()}")
        else:
            print(f"  [FAIL] {r['page']}: {r['error']}")

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

    # 生成 index.html 目录页
    if not args.skip_index:
        pages_info = []
        for i, page_config in enumerate(pages):
            page_info = {
                'page_name': page_config.get('page_name', ''),
                'page_type': page_config.get('page_type', 'list'),
                'description': page_config.get('clarification', {}).get('description', '')
                  if isinstance(page_config.get('clarification'), dict)
                  else '',
            }
            # 从生成结果中提取文件名
            if i < len(results) and results[i]['status'] == 'success':
                try:
                    result_data = json.loads(results[i]['output'])
                    page_info['file_name'] = result_data.get('file_name', '')
                except (json.JSONDecodeError, KeyError):
                    page_info['file_name'] = ''
            pages_info.append(page_info)

        index_path = generate_index_html(output_path, pages_info)
        print(f'目录页已生成: {index_path}')


if __name__ == '__main__':
    main()
