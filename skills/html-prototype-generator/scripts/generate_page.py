#!/usr/bin/env python3
"""
generate_page.py - 骨架填槽模式，从 page-skeleton.html 读取骨架，填入 SLOT 数据后输出。

用法：
  python generate_page.py --input '{...}' 或 --config page_config.json

输入 JSON 结构：
{
  "page_name": "角色列表",
  "page_type": "list",
  "scenario": "new",          // new | refactor
  "output_path": ".dev/prototype",
  "slots": {
    "page_title": "角色管理",
    "sidebar_items": "<li>...</li>",
    "filter_fields": "<input ...>",
    "filter_buttons": "<button ...>",
    "table_thead": "<th ...>",
    "table_tbody": "<tr ...>",
    "total_count": "50",
    "drawer_width": "980px",
    "drawer_form_fields": "<div class='ant-form-item'>...</div>",
    "doc_content": "<div>...</div>",
    "guide_steps": "{ id:1, selector:'#btn', type:'new', title:'新增：按钮', desc:'说明' },"
  }
}
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
ASSETS_DIR = SCRIPT_DIR.parent / 'assets'
SKELETON_PATH = ASSETS_DIR / 'page-skeleton.html'
BASE_CSS_PATH = ASSETS_DIR / 'base.css'
GUIDE_JS_PATH = ASSETS_DIR / 'guide-layer.js'


def load_assets():
    """加载三个固定资产文件，任一缺失则报错。"""
    missing = []
    for p in [SKELETON_PATH, BASE_CSS_PATH, GUIDE_JS_PATH]:
        if not p.exists():
            missing.append(str(p))
    if missing:
        raise FileNotFoundError(f"缺少固定资产文件：{', '.join(missing)}")

    skeleton = SKELETON_PATH.read_text(encoding='utf-8')
    base_css = BASE_CSS_PATH.read_text(encoding='utf-8')
    guide_js = GUIDE_JS_PATH.read_text(encoding='utf-8')
    return skeleton, base_css, guide_js


def fill_slots(skeleton: str, slots: dict, base_css: str, guide_js: str) -> str:
    """将骨架中的所有 SLOT 占位符替换为实际内容。"""
    # 注入固定资产（不经过 slots 字典，防止被覆盖）
    # 处理注释格式 <!--SLOT:base_css (...)-->
    html = re.sub(
        r'<!--SLOT:base_css[^>]*-->',
        base_css,
        skeleton
    )
    html = re.sub(
        r'<!--SLOT:guide_layer_js[^>]*-->',
        guide_js,
        html
    )

    # 注入 page_name（标题用）
    page_name = slots.get('page_name', '页面')
    html = html.replace('<!--SLOT:page_name-->', page_name)

    # 注入 guide_steps（在 JS 块内）
    guide_steps_content = slots.get('guide_steps', '// 无改动').strip()
    # 去掉首尾的逗号，避免 JS 语法错误
    html = html.replace('<!--SLOT:guide_steps-->', guide_steps_content)

    # 注入其余普通 SLOT
    slot_map = {
        'page_title':          slots.get('page_title', page_name),
        'sidebar_items':       slots.get('sidebar_items', _default_sidebar(page_name)),
        'filter_fields':       slots.get('filter_fields', ''),
        'filter_buttons':      slots.get('filter_buttons', _default_filter_buttons()),
        'table_thead':         slots.get('table_thead', _default_thead()),
        'table_tbody':         slots.get('table_tbody', _default_tbody()),
        'total_count':         str(slots.get('total_count', '0')),
        'drawer_width':        slots.get('drawer_width', '980px'),
        'drawer_form_fields':  slots.get('drawer_form_fields', ''),
        'doc_content':         slots.get('doc_content', _default_doc(page_name)),
    }

    for key, value in slot_map.items():
        html = html.replace(f'<!--SLOT:{key}-->', value)

    return html


# ── 默认内容生成函数（仅在调用方未提供对应 slot 时使用）─────────────────────

def _default_sidebar(page_name: str) -> str:
    return (
        '<li style="padding: 10px 20px; color: rgba(255,255,255,.65); cursor: pointer; '
        'font-size: 14px; display: flex; align-items: center;">'
        '<span class="anticon anticon-home" style="margin-right: 10px; font-size: 14px;"></span>首页</li>'
        f'<li style="padding: 10px 16px; background: #3e8dff; color: #fff; cursor: pointer; '
        f'font-size: 14px; border-radius: 4px; margin: 0 8px; display: flex; align-items: center;">'
        f'<span class="anticon anticon-file-text" style="margin-right: 10px; font-size: 14px;"></span>{page_name}</li>'
    )


def _default_filter_buttons() -> str:
    return (
        '<button class="ant-btn ant-btn-primary" onclick="mockAction(\'查询\')">查询</button>'
        '<button class="ant-btn" onclick="mockAction(\'重置\')">重置</button>'
    )


def _default_thead() -> str:
    return (
        '<th class="ant-table-cell" style="text-align: center; width: 60px;">序号</th>'
        '<th class="ant-table-cell">名称</th>'
        '<th class="ant-table-cell" style="width: 120px;">状态</th>'
        '<th class="ant-table-cell" style="text-align: center; width: 180px;">操作</th>'
    )


def _default_tbody() -> str:
    rows = []
    for i in range(1, 4):
        rows.append(
            f'<tr class="ant-table-row">'
            f'<td class="ant-table-cell" style="text-align: center;">{i}</td>'
            f'<td class="ant-table-cell">示例数据 {i}</td>'
            f'<td class="ant-table-cell">'
            f'<span class="kt-status kt-status-success"><span class="kt-status-dot"></span>启用</span>'
            f'</td>'
            f'<td class="ant-table-cell" style="text-align: center;">'
            f'<div class="action-group">'
            f'<a style="color: #3e8dff; cursor: pointer;" onclick="openDrawer(\'详情\', \'detail\')">详情</a>'
            f'<span class="action-divider"></span>'
            f'<a style="color: #3e8dff; cursor: pointer;" onclick="openDrawer(\'编辑\', \'edit\')">编辑</a>'
            f'<span class="action-divider"></span>'
            f'<a style="color: #ff4d4f; cursor: pointer;" onclick="openConfirmModal()">删除</a>'
            f'</div>'
            f'</td>'
            f'</tr>'
        )
    return '\n'.join(rows)


def _default_doc(page_name: str) -> str:
    return (
        '<div style="background: #fff; border-radius: 8px; padding: 16px; margin-bottom: 12px;">'
        '<div style="font-size: 15px; font-weight: 600; color: rgba(0,0,0,.85); margin-bottom: 12px; '
        'padding-bottom: 8px; border-bottom: 1px solid #f0f0f0;">页面说明</div>'
        f'<p style="color: rgba(0,0,0,.65); font-size: 14px; margin: 0;">{page_name}，支持数据的查询、新增、编辑和删除。</p>'
        '</div>'
        '<div style="background: #fff; border-radius: 8px; padding: 16px; margin-bottom: 12px;">'
        '<div style="font-size: 15px; font-weight: 600; color: rgba(0,0,0,.85); margin-bottom: 12px; '
        'padding-bottom: 8px; border-bottom: 1px solid #f0f0f0;">交互逻辑</div>'
        '<div style="font-size: 14px; color: rgba(0,0,0,.65); line-height: 2;">'
        '<div><b>查询：</b>填写筛选条件后点击查询</div>'
        '<div><b>新增：</b>点击新增按钮打开右侧抽屉</div>'
        '<div><b>编辑：</b>点击编辑打开抽屉并回填数据</div>'
        '<div><b>删除：</b>弹出确认弹窗，确认后删除</div>'
        '</div>'
        '</div>'
    )


# ── 文件名生成 ────────────────────────────────────────────────────────────────

def generate_filename(page_name: str, scenario: str, output_dir: str, version=None) -> str:
    date_str = datetime.now().strftime('%Y%m%d')
    safe_name = re.sub(r'[^\w\u4e00-\u9fff-]', '-', page_name).strip('-')

    if scenario == 'refactor' and version:
        filename = f'prototype-{date_str}-{safe_name}-v{version}.html'
    else:
        filename = f'prototype-{date_str}-{safe_name}.html'

    full_path = os.path.join(output_dir, filename)
    if os.path.exists(full_path):
        v = 2
        while os.path.exists(os.path.join(output_dir, f'prototype-{date_str}-{safe_name}-v{v}.html')):
            v += 1
        filename = f'prototype-{date_str}-{safe_name}-v{v}.html'

    return filename


# ── 主流程 ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='骨架填槽模式生成HTML原型')
    parser.add_argument('--input', help='JSON 配置字符串')
    parser.add_argument('--config', help='JSON 配置文件路径')
    args = parser.parse_args()

    if args.config:
        with open(args.config, 'r', encoding='utf-8') as f:
            config = json.load(f)
    elif args.input:
        config = json.loads(args.input)
    else:
        print('错误: 请提供 --input 或 --config', file=sys.stderr)
        sys.exit(1)

    output_dir = config.get('output_path', '.dev/prototype')
    os.makedirs(output_dir, exist_ok=True)

    try:
        skeleton, base_css, guide_js = load_assets()
    except FileNotFoundError as e:
        print(f'错误: {e}', file=sys.stderr)
        sys.exit(1)

    page_name = config.get('page_name', '页面')
    slots = config.get('slots', {})
    slots['page_name'] = page_name

    html = fill_slots(skeleton, slots, base_css, guide_js)

    filename = generate_filename(
        page_name,
        config.get('scenario', 'new'),
        output_dir,
        config.get('version')
    )
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

    result = {
        'file_path': filepath,
        'file_name': filename,
        'status': 'success',
        'page_info': {
            'name': page_name,
            'type': config.get('page_type', 'list'),
        }
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
