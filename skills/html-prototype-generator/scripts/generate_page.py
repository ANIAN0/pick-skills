#!/usr/bin/env python3
"""
generate_page.py - 根据配置生成HTML原型页面。

用法：
  python generate_page.py --input '{
    "page_name": "角色列表",
    "page_type": "list",
    "scenario": "new",
    "output_path": ".dev/prototype",
    "clarification": {...}
  }'

  或指定配置文件：
  python generate_page.py --config page_config.json
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime


# 项目配色常量
COLORS = {
    'primary': '#3e8dff',
    'primary_bg': '#d6e7ff',
    'primary_hover': '#5ea3ff',
    'success': '#00e5c7',
    'success_bg': '#effffb',
    'danger': '#ff8b78',
    'danger_bg': '#fff5f3',
    'warning': '#ffb71d',
    'warning_bg': '#fff2d6',
    'default': '#bfc6d1',
    'default_bg': '#f5f6f9',
    'sidebar': '#1e202a',
    'content_bg': '#f0f2f5',
}

ANTD_CSS_CDN = 'https://cdnjs.cloudflare.com/ajax/libs/antd/4.24.15/antd.min.css'
TAILWIND_CDN = 'https://cdn.tailwindcss.com'


def generate_css_variables():
    """生成 CSS 变量和覆盖样式"""
    return f"""
    :root {{
      --kt-primary: {COLORS['primary']};
      --kt-primary-bg: {COLORS['primary_bg']};
      --kt-success: {COLORS['success']};
      --kt-success-bg: {COLORS['success_bg']};
      --kt-danger: {COLORS['danger']};
      --kt-danger-bg: {COLORS['danger_bg']};
      --kt-warning: {COLORS['warning']};
      --kt-warning-bg: {COLORS['warning_bg']};
      --kt-default: {COLORS['default']};
      --kt-default-bg: {COLORS['default_bg']};
      --kt-sidebar: {COLORS['sidebar']};
      --kt-content-bg: {COLORS['content_bg']};
    }}

    .ant-btn-primary {{ background-color: {COLORS['primary']}; border-color: {COLORS['primary']}; }}
    .ant-btn-primary:hover {{ background-color: {COLORS['primary_hover']}; border-color: {COLORS['primary_hover']}; }}
    .ant-btn-primary:active {{ background-color: #2a75d4; border-color: #2a75d4; }}
    a, .ant-btn-link {{ color: {COLORS['primary']}; }}
    a:hover, .ant-btn-link:hover {{ color: {COLORS['primary_hover']}; }}

    .kt-status {{ display: inline-flex; align-items: center; gap: 6px; padding: 0 8px; height: 24px; border-radius: 4px; font-size: 12px; line-height: 24px; }}
    .kt-status-dot {{ width: 6px; height: 6px; border-radius: 50%; display: inline-block; }}
    .kt-status-primary {{ background: {COLORS['primary_bg']}; color: {COLORS['primary']}; }}
    .kt-status-primary .kt-status-dot {{ background: {COLORS['primary']}; }}
    .kt-status-success {{ background: {COLORS['success_bg']}; color: #00a89a; }}
    .kt-status-success .kt-status-dot {{ background: {COLORS['success']}; }}
    .kt-status-danger {{ background: {COLORS['danger_bg']}; color: #d4634f; }}
    .kt-status-danger .kt-status-dot {{ background: {COLORS['danger']}; }}
    .kt-status-warning {{ background: {COLORS['warning_bg']}; color: #c99200; }}
    .kt-status-warning .kt-status-dot {{ background: {COLORS['warning']}; }}
    .kt-status-default {{ background: {COLORS['default_bg']}; color: #8c95a6; }}
    .kt-status-default .kt-status-dot {{ background: {COLORS['default']}; }}

    .tl-main {{ flex: 1; overflow: auto; display: flex; flex-direction: column; gap: 0; }}
    .tl-filter {{ background: #fff; padding: 16px 24px; border-radius: 8px; margin-bottom: 16px; }}
    .tl-filter-left {{ display: flex; flex-wrap: wrap; align-items: center; gap: 12px; }}
    .tl-table {{ background: #fff; padding: 24px; padding-top: 16px; border-radius: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }}

    .action-group {{ display: inline-flex; align-items: center; gap: 0; }}
    .action-group .ant-btn-link {{ padding: 0 4px; height: auto; }}
    .action-group .action-divider {{ width: 1px; height: 14px; background: #e8e8e8; margin: 0 4px; }}

    .doc-toggle {{ position: fixed; top: 50%; right: 0; transform: translateY(-50%); z-index: 1001; background: {COLORS['primary']}; color: #fff; border: none; padding: 12px 4px; border-radius: 4px 0 0 4px; cursor: pointer; writing-mode: vertical-rl; font-size: 13px; letter-spacing: 2px; transition: right 0.3s; }}
    .doc-panel {{ position: fixed; top: 0; right: -400px; width: 400px; height: 100vh; background: #fafafa; border-left: 1px solid #e8e8e8; padding: 24px; overflow-y: auto; z-index: 1000; transition: right 0.3s; }}
    .doc-panel.open {{ right: 0; }}
    .doc-panel .doc-section {{ background: #fff; border-radius: 8px; padding: 16px; margin-bottom: 12px; }}
    .doc-panel .doc-title {{ font-size: 15px; font-weight: 600; color: rgba(0,0,0,0.85); margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #f0f0f0; }}
    """


def generate_sidebar(menu_items, active_item):
    """生成侧边栏 HTML"""
    menu_html = ''
    for item in menu_items:
        is_active = item.get('name') == active_item
        icon = item.get('icon', '📋')
        style = f'padding: 10px 16px; background: {COLORS["primary"]}; color: #fff; font-size: 14px; cursor: pointer; border-radius: 4px; margin: 0 8px;' if is_active else f'padding: 10px 20px; color: rgba(255,255,255,0.65); font-size: 14px; cursor: pointer;'
        menu_html += f'      <li style="{style}"><span style="margin-right: 10px;">{icon}</span>{item["name"]}</li>\n'

    return f"""  <aside style="background: {COLORS['sidebar']}; width: 220px; flex-shrink: 0; position: fixed; left: 0; top: 0; bottom: 0; z-index: 100;">
    <div style="height: 56px; display: flex; align-items: center; padding: 0 20px; border-bottom: 1px solid rgba(255,255,255,0.08);">
      <span style="color: #fff; font-size: 16px; font-weight: 600;">KT Agent</span>
    </div>
    <ul style="list-style: none; padding: 8px 0; margin: 0;">
{menu_html}    </ul>
  </aside>"""


def generate_header(title):
    """生成顶栏 HTML"""
    return f"""  <header style="height: 56px; background: #fff; padding: 0 24px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 1px 4px rgba(0,21,41,0.08); position: sticky; top: 0; z-index: 99;">
      <span style="font-size: 16px; font-weight: 500; color: rgba(0,0,0,0.85);">{title}</span>
      <div style="display: flex; align-items: center; gap: 16px;">
        <span style="color: rgba(0,0,0,0.65); font-size: 14px;">管理员</span>
      </div>
    </header>"""


def generate_filter_fields(fields):
    """生成筛选字段 HTML"""
    html = ''
    for field in fields:
        ftype = field.get('type', 'input')
        label = field.get('label', '')
        placeholder = field.get('placeholder', f'请输入{label}')
        width = field.get('width', '200px')

        if ftype == 'input':
            html += f'      <input class="ant-input" placeholder="{placeholder}" style="width: {width};">\n'
        elif ftype == 'select':
            options = field.get('options', [])
            default = field.get('default', f'全部{label}')
            html += f'      <div class="ant-select ant-select-single" style="width: {width};">\n'
            html += f'        <div class="ant-select-selector"><span class="ant-select-selection-item">{default}</span></div>\n'
            html += f'      </div>\n'
        elif ftype == 'date':
            html += f'      <span class="ant-picker" style="width: 220px;"><span class="ant-picker-input"><input readonly placeholder="{placeholder}" style="border: none; outline: none; width: 100%;"></span></span>\n'

    return html


def generate_table_columns(columns):
    """生成表格列 HTML"""
    thead = ''
    for col in columns:
        title = col.get('title', '')
        width = col.get('width', '')
        align = col.get('align', 'left')
        width_style = f'width: {width};' if width else ''
        align_style = f'text-align: {align};' if align != 'left' else ''
        style = f'{width_style} {align_style}'.strip()
        style_attr = f' style="{style}"' if style else ''
        thead += f'          <th class="ant-table-cell"{style_attr}>{title}</th>\n'
    return thead


def generate_table_rows(columns, rows):
    """生成表格行 HTML"""
    html = ''
    for i, row in enumerate(rows, 1):
        html += '        <tr class="ant-table-row">\n'
        for col in columns:
            data_index = col.get('dataIndex', '')
            col_type = col.get('type', 'text')
            value = row.get(data_index, '')

            if col_type == 'status':
                status_type = row.get(f'{data_index}_type', 'default')
                html += f'          <td class="ant-table-cell"><span class="kt-status kt-status-{status_type}"><span class="kt-status-dot"></span>{value}</span></td>\n'
            elif col_type == 'action':
                actions = col.get('actions', ['详情', '编辑', '删除'])
                action_html = ''
                for j, action in enumerate(actions):
                    if j > 0:
                        action_html += '<span class="action-divider"></span>'
                    is_delete = '删除' in action
                    color = '#ff4d4f' if is_delete else COLORS['primary']
                    click = f'openConfirmModal()' if is_delete else f'openDrawer(\'{action}\', \'edit\')'
                    action_html += f'<a style="color: {color}; cursor: pointer;" onclick="{click}">{action}</a>'
                html += f'          <td class="ant-table-cell" style="text-align: center;"><div class="action-group">{action_html}</div></td>\n'
            elif col_type == 'index':
                html += f'          <td class="ant-table-cell" style="text-align: center;">{i}</td>\n'
            else:
                html += f'          <td class="ant-table-cell">{value}</td>\n'
        html += '        </tr>\n'
    return html


def generate_form_fields(fields):
    """生成表单字段 HTML"""
    html = ''
    for field in fields:
        label = field.get('label', '')
        ftype = field.get('type', 'input')
        required = field.get('required', False)
        placeholder = field.get('placeholder', f'请输入{label}')
        disabled = field.get('disabled', False)

        required_html = '<span style="color: #ff4d4f; margin-right: 4px;">*</span>' if required else ''
        disabled_attr = 'disabled' if disabled else ''

        html += f'    <div class="ant-form-item">\n'
        html += f'      <div class="ant-form-item-label"><label>{required_html}{label}</label></div>\n'
        html += f'      <div class="ant-form-item-control"><div class="ant-form-item-control-input">\n'

        if ftype in ('input', 'number'):
            html += f'        <input class="ant-input" placeholder="{placeholder}" style="max-width: 400px;" {disabled_attr}>\n'
        elif ftype == 'textarea':
            html += f'        <textarea class="ant-input" placeholder="{placeholder}" rows="3" style="max-width: 400px; resize: vertical;" {disabled_attr}></textarea>\n'
        elif ftype == 'select':
            html += f'        <div class="ant-select ant-select-single" style="width: 200px;"><div class="ant-select-selector"><span class="ant-select-selection-item">{placeholder}</span></div></div>\n'
        elif ftype == 'switch':
            html += f'        <button class="ant-switch" type="button"></button>\n'

        html += f'      </div></div>\n'
        html += f'    </div>\n'

    return html


def generate_list_page(config):
    """生成列表页 HTML"""
    page_name = config.get('page_name', '页面')
    clarification = config.get('clarification', {})
    layout = clarification.get('layout', {})
    data = clarification.get('data', {})
    interactions = clarification.get('interactions', {})

    # 筛选字段
    filter_fields = layout.get('filter_fields', [])
    filter_buttons = layout.get('filter_buttons', ['查询', '重置'])
    action_buttons = layout.get('action_buttons', [])

    # 表格
    columns = data.get('columns', [{'title': '名称', 'dataIndex': 'name', 'type': 'text'}])
    rows = data.get('rows', [{'name': '示例数据'}])
    total = data.get('total', len(rows))

    # 抽屉
    drawer_width = layout.get('drawer_width', '980px')
    form_fields = data.get('form_fields', [])

    # 菜单
    menu_items = layout.get('menu_items', [
        {'name': '首页', 'icon': '🏠'},
        {'name': page_name, 'icon': '📋'},
    ])

    # 生成筛选区
    filter_html = generate_filter_fields(filter_fields)
    filter_btn_html = ''
    for btn in filter_buttons:
        if btn == '查询':
            filter_btn_html += f'      <button class="ant-btn ant-btn-primary" onclick="mockAction(\'查询\')">{btn}</button>\n'
        else:
            filter_btn_html += f'      <button class="ant-btn">{btn}</button>\n'
    for btn in action_buttons:
        filter_btn_html += f'      <button class="ant-btn ant-btn-primary" onclick="openDrawer(\'{btn}\', \'add\')">{btn}</button>\n'

    # 生成表格
    thead_html = generate_table_columns(columns)
    tbody_html = generate_table_rows(columns, rows)

    # 生成表单
    form_html = generate_form_fields(form_fields)

    # 生成文档内容
    doc_content = generate_doc_content(page_name, clarification)

    # 组装完整 HTML
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>原型 - {page_name}</title>
  <link rel="stylesheet" href="{ANTD_CSS_CDN}">
  <script src="{TAILWIND_CDN}"></script>
  <style>{generate_css_variables()}
  </style>
</head>
<body>
<div class="ant-layout" style="min-height: 100vh;">
{generate_sidebar(menu_items, page_name)}
  <div style="margin-left: 220px; flex: 1; display: flex; flex-direction: column;">
{generate_header(page_name)}
    <main style="flex: 1; padding: 16px; background: {COLORS['content_bg']}; overflow: auto;">
      <div class="tl-filter">
        <div class="tl-filter-left">
{filter_html}{filter_btn_html}      </div>
      </div>

      <div class="tl-table">
        <div class="ant-table-wrapper">
          <div class="ant-table">
            <div class="ant-table-container">
              <div class="ant-table-content">
                <table style="table-layout: auto; width: 100%;">
                  <thead class="ant-table-thead">
                    <tr>
{thead_html}                    </tr>
                  </thead>
                  <tbody class="ant-table-tbody">
{tbody_html}                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
        <div style="padding: 16px 0 0; display: flex; justify-content: flex-end;">
          <ul class="ant-pagination">
            <li class="ant-pagination-total-text">共 {total} 条</li>
            <li class="ant-pagination-prev ant-pagination-disabled"><button class="ant-pagination-item-link" disabled>&lt;</button></li>
            <li class="ant-pagination-item ant-pagination-item-active"><a>1</a></li>
            <li class="ant-pagination-next"><button class="ant-pagination-item-link">&gt;</button></li>
          </ul>
        </div>
      </div>
    </main>
  </div>
</div>

<!-- 抽屉 -->
<div id="drawer" style="display: none;">
  <div class="ant-drawer" style="position: fixed; top: 0; right: 0; bottom: 0; z-index: 1000;">
    <div class="ant-drawer-mask" onclick="closeDrawer()" style="background: rgba(0,0,0,0.45); position: fixed; inset: 0;"></div>
    <div class="ant-drawer-content-wrapper" style="width: {drawer_width}; position: fixed; top: 0; right: 0; bottom: 0;">
      <div class="ant-drawer-content">
        <div class="ant-drawer-wrapper-body" style="display: flex; flex-direction: column; height: 100%;">
          <div class="ant-drawer-header" style="padding: 16px 24px; border-bottom: 1px solid #f0f0f0; display: flex; align-items: center; justify-content: space-between;">
            <div class="ant-drawer-title" id="drawerTitle" style="font-size: 16px; font-weight: 500;">新增</div>
            <button onclick="closeDrawer()" style="border: none; background: none; font-size: 16px; cursor: pointer; color: rgba(0,0,0,0.45);">✕</button>
          </div>
          <div class="ant-drawer-body" style="flex: 1; overflow: auto; padding: 24px;">
            <form class="ant-form ant-form-vertical">
{form_html}            </form>
          </div>
          <div class="ant-drawer-footer" id="drawerFooter" style="border-top: 1px solid #f0f0f0; padding: 12px 24px; text-align: right;">
            <button class="ant-btn" style="margin-right: 8px;" onclick="closeDrawer()">取消</button>
            <button class="ant-btn ant-btn-primary">保存</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- 确认弹窗 -->
<div id="confirmModal" style="display: none;">
  <div class="ant-modal-mask" style="background: rgba(0,0,0,0.45); position: fixed; inset: 0; z-index: 1001;"></div>
  <div class="ant-modal-wrap" style="position: fixed; inset: 0; z-index: 1002; display: flex; align-items: center; justify-content: center;">
    <div class="ant-modal" style="width: 420px;">
      <div class="ant-modal-content">
        <div class="ant-modal-header"><div class="ant-modal-title">确认删除</div></div>
        <div class="ant-modal-body" style="padding: 24px;"><p>确定要删除此记录吗？此操作不可撤销。</p></div>
        <div class="ant-modal-footer">
          <button class="ant-btn" onclick="closeConfirmModal()">取消</button>
          <button class="ant-btn ant-btn-primary" style="background: #ff4d4f; border-color: #ff4d4f;">确认删除</button>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- 文档面板 -->
<button class="doc-toggle" onclick="toggleDoc()">交互说明</button>
<div class="doc-panel" id="docPanel">
{doc_content}
</div>

<script>
function openDrawer(title, mode) {{
  document.getElementById('drawer').style.display = 'block';
  document.getElementById('drawerTitle').textContent = title;
  const footer = document.getElementById('drawerFooter');
  if (mode === 'detail') {{
    footer.innerHTML = '<button class="ant-btn" onclick="closeDrawer()">返回</button>';
  }} else {{
    footer.innerHTML = '<button class="ant-btn" style="margin-right:8px" onclick="closeDrawer()">取消</button><button class="ant-btn ant-btn-primary">保存</button>';
  }}
}}
function closeDrawer() {{ document.getElementById('drawer').style.display = 'none'; }}
function openConfirmModal() {{ document.getElementById('confirmModal').style.display = 'block'; }}
function closeConfirmModal() {{ document.getElementById('confirmModal').style.display = 'none'; }}
function toggleDoc() {{ document.getElementById('docPanel').classList.toggle('open'); }}
function mockAction(action, data) {{ console.log('[Mock]', action, data); }}
</script>
</body>
</html>"""

    return html


def generate_doc_content(page_name, clarification):
    """生成文档面板内容"""
    interactions = clarification.get('interactions', {})
    data = clarification.get('data', {})

    doc_html = f"""  <div class="doc-section">
    <div class="doc-title">页面说明</div>
    <p style="color: rgba(0,0,0,0.65); font-size: 14px;">{page_name}，支持数据的查询、新增、编辑和删除操作。</p>
  </div>
  <div class="doc-section">
    <div class="doc-title">交互逻辑</div>
    <div style="font-size: 14px; color: rgba(0,0,0,0.65); line-height: 2;">
      <div><b>查询：</b>输入筛选条件后点击查询按钮筛选列表</div>
      <div><b>重置：</b>清空筛选条件恢复默认列表</div>
      <div><b>新增：</b>点击新增按钮打开右侧抽屉填写表单</div>
      <div><b>编辑：</b>点击编辑打开抽屉并回填数据</div>
      <div><b>删除：</b>弹出确认弹窗，确认后删除</div>
      <div><b>详情：</b>点击详情打开只读抽屉</div>
    </div>
  </div>"""

    # 字段说明
    columns = data.get('columns', [])
    if columns:
        doc_html += '\n  <div class="doc-section">\n    <div class="doc-title">字段说明</div>\n'
        doc_html += '    <table style="width: 100%; font-size: 13px; border-collapse: collapse;">\n'
        doc_html += '      <tr style="border-bottom: 1px solid #f0f0f0;"><th style="text-align: left; padding: 6px 0; color: rgba(0,0,0,0.85);">列名</th><th style="text-align: left; padding: 6px 0; color: rgba(0,0,0,0.85);">字段</th></tr>\n'
        for col in columns:
            title = col.get('title', '')
            data_index = col.get('dataIndex', '')
            if title and data_index:
                doc_html += f'      <tr style="border-bottom: 1px solid #f0f0f0;"><td style="padding: 6px 0; color: rgba(0,0,0,0.65);">{title}</td><td style="padding: 6px 0; color: rgba(0,0,0,0.45);">{data_index}</td></tr>\n'
        doc_html += '    </table>\n  </div>'

    return doc_html


def generate_output_filename(page_name, scenario, output_dir, version=None):
    """生成输出文件名"""
    date_str = datetime.now().strftime('%Y%m%d')
    safe_name = re.sub(r'[^\w一-鿿-]', '-', page_name).strip('-')

    if scenario == 'refactor' and version:
        filename = f'prototype-{date_str}-{safe_name}-v{version}.html'
    else:
        filename = f'prototype-{date_str}-{safe_name}.html'

    # 检查文件是否已存在，如果存在则递增版本号
    full_path = os.path.join(output_dir, filename)
    if os.path.exists(full_path) and scenario != 'refactor':
        v = 2
        while os.path.exists(os.path.join(output_dir, f'prototype-{date_str}-{safe_name}-v{v}.html')):
            v += 1
        filename = f'prototype-{date_str}-{safe_name}-v{v}.html'

    return filename


def main():
    parser = argparse.ArgumentParser(description='生成HTML原型页面')
    parser.add_argument('--input', help='JSON 配置字符串')
    parser.add_argument('--config', help='JSON 配置文件路径')
    args = parser.parse_args()

    if args.config:
        with open(args.config, 'r', encoding='utf-8') as f:
            config = json.load(f)
    elif args.input:
        config = json.loads(args.input)
    else:
        print('错误: 请提供 --input 或 --config 参数', file=sys.stderr)
        sys.exit(1)

    page_type = config.get('page_type', 'list')
    output_dir = config.get('output_path', '.dev/prototype')

    os.makedirs(output_dir, exist_ok=True)

    if page_type == 'list':
        html = generate_list_page(config)
    else:
        # 其他类型暂使用列表页模板
        html = generate_list_page(config)

    filename = generate_output_filename(
        config.get('page_name', 'page'),
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
        'message': '生成成功',
        'page_info': {
            'name': config.get('page_name', ''),
            'type': page_type,
        }
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
