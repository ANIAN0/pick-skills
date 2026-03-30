"""
原型HTML生成辅助脚本
用于生成符合Ant Design风格的HTML原型页面
"""

from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import json


class PrototypeTemplate:
    """原型HTML模板生成器"""

    # Ant Design 配色
    COLORS = {
        'primary': '#1677ff',
        'primary_hover': '#4096ff',
        'primary_active': '#0958d9',
        'success': '#52c41a',
        'warning': '#faad14',
        'error': '#f5222d',
        'info': '#1677ff',
        'text': 'rgba(0, 0, 0, 0.88)',
        'text_secondary': 'rgba(0, 0, 0, 0.45)',
        'border': '#d9d9d9',
        'bg': '#f5f5f5',
        'white': '#ffffff',
    }

    @staticmethod
    def generate_base_html(title: str, prototype_content: str, description_content: str) -> str:
        """生成基础HTML框架"""
        return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>原型 - {title}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      theme: {{
        extend: {{
          colors: {{
            primary: '{PrototypeTemplate.COLORS["primary"]}',
            'primary-hover': '{PrototypeTemplate.COLORS["primary_hover"]}',
            'primary-active': '{PrototypeTemplate.COLORS["primary_active"]}',
            success: '{PrototypeTemplate.COLORS["success"]}',
            warning: '{PrototypeTemplate.COLORS["warning"]}',
            error: '{PrototypeTemplate.COLORS["error"]}',
            info: '{PrototypeTemplate.COLORS["info"]}',
          }}
        }}
      }}
    }}
  </script>
  <style>
    /* Ant Design 组件样式 */
    .ant-btn {{ @apply px-4 py-1.5 rounded text-sm font-medium transition-all cursor-pointer; }}
    .ant-btn-primary {{ @apply bg-primary text-white hover:opacity-90; }}
    .ant-btn-default {{ @apply bg-white border border-gray-300 text-gray-700 hover:border-primary hover:text-primary; }}
    .ant-btn-danger {{ @apply bg-error text-white hover:opacity-90; }}
    .ant-input {{ @apply px-3 py-1.5 border border-gray-300 rounded hover:border-primary focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all; }}
    .ant-select {{ @apply px-3 py-1.5 border border-gray-300 rounded bg-white hover:border-primary cursor-pointer outline-none; }}
    .ant-table {{ @apply w-full text-sm; }}
    .ant-table th {{ @apply bg-gray-50 px-4 py-3 text-left font-medium text-gray-600 border-b border-gray-200; }}
    .ant-table td {{ @apply px-4 py-3 text-gray-700 border-b border-gray-100; }}
    .ant-table tr:hover td {{ @apply bg-gray-50; }}
    .ant-tag {{ @apply inline-flex items-center px-2 py-0.5 text-xs rounded; }}
    .ant-tag-blue {{ @apply bg-blue-50 text-blue-600 border border-blue-200; }}
    .ant-tag-green {{ @apply bg-green-50 text-green-600 border border-green-200; }}
    .ant-tag-orange {{ @apply bg-orange-50 text-orange-600 border border-orange-200; }}
    .ant-tag-red {{ @apply bg-red-50 text-red-600 border border-red-200; }}
    .ant-tag-gray {{ @apply bg-gray-100 text-gray-600 border border-gray-200; }}
    .ant-card {{ @apply bg-white rounded border border-gray-200 shadow-sm; }}
    .ant-divider {{ @apply h-px bg-gray-200 my-4; }}
    .ant-empty {{ @apply flex flex-col items-center justify-center py-12 text-gray-400; }}
    .ant-spin {{ @apply inline-block w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin; }}
    .ant-message {{ @apply fixed top-4 left-1/2 transform -translate-x-1/2 px-4 py-2 rounded shadow-lg z-50 transition-all; }}
    .ant-message-success {{ @apply bg-green-50 text-green-600 border border-green-200; }}
    .ant-message-error {{ @apply bg-red-50 text-red-600 border border-red-200; }}
    .ant-drawer-mask {{ @apply fixed inset-0 bg-black/45 transition-opacity z-40; }}
    .ant-drawer {{ @apply fixed inset-y-0 right-0 bg-white shadow-2xl transition-transform z-50; }}
  </style>
</head>
<body class="bg-gray-100">
  <div class="flex h-screen">
    <!-- 左侧：原型页面 -->
    <div class="w-[1200px] bg-white overflow-auto flex flex-col">
{prototype_content}
    </div>

    <!-- 右侧：原型说明 -->
    <div class="flex-1 bg-gray-50 p-6 overflow-auto">
{description_content}
    </div>
  </div>

  <script>
    // Mock 交互函数
    function mockAction(action, data) {{
      console.log('[Mock]', action, data);
      showMessage(action + ' 成功（模拟）', 'success');
    }}

    function showMessage(text, type = 'success') {{
      const msg = document.createElement('div');
      msg.className = `ant-message ant-message-${{type}}`;
      msg.textContent = text;
      document.body.appendChild(msg);
      setTimeout(() => {{
        msg.style.opacity = '0';
        setTimeout(() => msg.remove(), 300);
      }}, 2000);
    }}
  </script>
</body>
</html>'''

    @staticmethod
    def generate_list_page(
        title: str,
        columns: List[Dict],
        search_fields: List[Dict],
        actions: List[str] = None,
        mock_data: List[Dict] = None
    ) -> str:
        """生成列表页原型内容"""
        # 构建搜索区域
        search_html = '<div class="flex flex-wrap gap-3">\n'
        for field in search_fields:
            if field.get('type') == 'select':
                options = ''.join([f'<option>{opt}</option>' for opt in field.get('options', [])])
                search_html += f'          <select class="ant-select w-32"><option>全部{field["label"]}</option>{options}</select>\n'
            else:
                search_html += f'          <input type="text" class="ant-input w-48" placeholder="请输入{field["label"]}">\n'
        search_html += '''          <button class="ant-btn ant-btn-primary" onclick="mockAction('搜索')">搜索</button>
          <button class="ant-btn ant-btn-default" onclick="mockAction('重置')">重置</button>
        </div>'''

        # 构建操作按钮
        actions_html = ''
        if actions:
            actions_html = '<div class="flex gap-2">\n'
            for action in actions:
                btn_class = 'ant-btn-primary' if action in ['新增', '创建', '添加'] else 'ant-btn-default'
                actions_html += f'            <button class="ant-btn {btn_class}" onclick="mockAction(\'{action}\')">{action}</button>\n'
            actions_html += '          </div>'

        # 构建表格列
        th_html = ''.join([f'              <th>{col["title"]}</th>\n' for col in columns])

        # 构建表格数据
        tbody_html = ''
        if mock_data:
            for row in mock_data:
                tbody_html += '            <tr>\n'
                for col in columns:
                    value = row.get(col['dataIndex'], '')
                    if col.get('render') == 'tag':
                        value = f'<span class="ant-tag ant-tag-{row.get(col["dataIndex"] + "_color", "blue")}">{value}</span>'
                    elif col.get('render') == 'actions':
                        value = '<a href="#" class="text-primary hover:underline" onclick="mockAction(\'编辑\', {{id: 1}})">编辑</a>'
                    tbody_html += f'              <td>{value}</td>\n'
                tbody_html += '            </tr>\n'
        else:
            tbody_html = '''            <tr>
              <td colspan="' + str(len(columns)) + '" class="ant-empty">
                <div class="text-4xl mb-2">📭</div>
                <div>暂无数据</div>
              </td>
            </tr>'''

        return f'''<div class="flex flex-col min-h-full">
  <!-- 顶栏 -->
  <header class="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6">
    <div class="flex items-center gap-4">
      <div class="w-8 h-8 bg-primary rounded flex items-center justify-center text-white font-bold">S</div>
      <span class="text-lg font-semibold">系统后台</span>
    </div>
    <div class="flex items-center gap-4">
      <span class="text-sm text-gray-600">管理员</span>
      <div class="w-8 h-8 bg-gray-200 rounded-full"></div>
    </div>
  </header>

  <div class="flex flex-1 overflow-hidden">
    <!-- 侧边栏 -->
    <aside class="w-52 bg-[#001529] text-white flex-shrink-0">
      <nav class="p-4 space-y-1">
        <a href="#" class="flex items-center gap-3 px-4 py-3 rounded hover:bg-white/10 text-white/70">
          <span>🏠</span>
          <span>首页</span>
        </a>
        <a href="#" class="flex items-center gap-3 px-4 py-3 rounded bg-primary text-white">
          <span>📋</span>
          <span>{title}</span>
        </a>
      </nav>
    </aside>

    <!-- 主内容 -->
    <main class="flex-1 overflow-auto bg-gray-50 p-6">
      <!-- 面包屑 -->
      <div class="mb-4 text-sm text-gray-500">
        <span>首页</span>
        <span class="mx-2">/</span>
        <span>{title}</span>
      </div>

      <div class="ant-card">
        <!-- 搜索区域 -->
        <div class="p-4 border-b border-gray-200">
{search_html}
        </div>

        <!-- 操作栏 -->
        <div class="p-4 border-b border-gray-200 flex justify-between items-center">
{actions_html}
        </div>

        <!-- 表格 -->
        <div class="overflow-x-auto">
          <table class="ant-table">
            <thead>
              <tr>
{th_html}              </tr>
            </thead>
            <tbody>
{tbody_html}            </tbody>
          </table>
        </div>

        <!-- 分页 -->
        <div class="p-4 border-t border-gray-200 flex justify-end items-center gap-4">
          <span class="text-sm text-gray-500">共 100 条</span>
          <div class="flex gap-1">
            <button class="px-3 py-1 border rounded hover:border-primary disabled:opacity-50" disabled>&lt;</button>
            <button class="px-3 py-1 border rounded bg-primary text-white">1</button>
            <button class="px-3 py-1 border rounded hover:border-primary">2</button>
            <button class="px-3 py-1 border rounded hover:border-primary">&gt;</button>
          </div>
        </div>
      </div>
    </main>
  </div>
</div>'''

    @staticmethod
    def generate_description(
        page_name: str,
        overview: str,
        sections: List[Dict]
    ) -> str:
        """生成原型说明文档内容"""
        sections_html = ''
        for i, section in enumerate(sections, 1):
            items_html = ''
            if 'items' in section:
                for item in section['items']:
                    items_html += f'''            <div class="flex gap-2">
              <span class="font-medium text-gray-700 min-w-[100px]">{item['label']}：</span>
              <span>{item['desc']}</span>
            </div>
'''

            sections_html += f'''        <div class="mb-6">
          <h4 class="text-base font-medium text-gray-800 mb-2">{i+1}. {section['title']}</h4>
          <div class="space-y-2 text-gray-600 text-sm">
{items_html}          </div>
        </div>
'''

        return f'''      <div class="max-w-2xl">
        <div class="mb-6">
          <h2 class="text-xl font-bold text-gray-800 mb-1">{page_name}原型说明</h2>
          <p class="text-sm text-gray-500">生成日期: {datetime.now().strftime('%Y-%m-%d')}</p>
        </div>

        <!-- 页面概述 -->
        <div class="mb-6">
          <h3 class="text-base font-semibold text-gray-800 mb-2 pb-2 border-b border-gray-200">1. 页面概述</h3>
          <p class="text-gray-600 text-sm leading-relaxed">{overview}</p>
        </div>

{sections_html}      </div>'''


def save_prototype(
    page_name: str,
    output_dir: str,
    prototype_content: str,
    description_content: str,
    scenario: str = 'new',
    old_file_name: Optional[str] = None
) -> Dict[str, str]:
    """保存原型HTML文件

    Args:
        page_name: 页面名称
        output_dir: 输出目录
        prototype_content: 原型内容HTML
        description_content: 说明文档HTML
        scenario: 'new' 或 'refactor'，决定文件名生成策略
        old_file_name: 旧文件名（场景B时使用）

    Returns:
        包含file_path, file_name, version等信息的字典
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 生成页面简称
    page_slug = page_name.lower().replace(' ', '-').replace('_', '-')

    if scenario == 'refactor' and old_file_name:
        # 场景B：改造原型，需要递增版本号
        # 解析旧文件名获取基础名称和版本号
        # 旧文件名格式: prototype-{日期}-{页面名}.html 或 prototype-{日期}-{页面名}-v{n}.html
        file_name = _generate_refactor_file_name(output_path, page_slug, old_file_name)
    else:
        # 场景A：新原型
        date_str = datetime.now().strftime('%Y%m%d')
        file_name = f"prototype-{date_str}-{page_slug}.html"

        # 检查是否存在同名文件，如果存在则添加版本号
        if (output_path / file_name).exists():
            file_name = _generate_versioned_file_name(output_path, page_slug, date_str)

    full_html = PrototypeTemplate.generate_base_html(
        title=page_name,
        prototype_content=prototype_content,
        description_content=description_content
    )

    file_path = output_path / file_name
    file_path.write_text(full_html, encoding='utf-8')

    # 提取版本号
    version = _extract_version_from_file_name(file_name)

    return {
        "file_path": str(file_path),
        "file_name": file_name,
        "version": version,
        "scenario": scenario
    }


def _generate_versioned_file_name(output_path: Path, page_slug: str, date_str: str) -> str:
    """生成带版本号的文件名，自动递增版本"""
    version = 2
    while True:
        file_name = f"prototype-{date_str}-{page_slug}-v{version}.html"
        if not (output_path / file_name).exists():
            return file_name
        version += 1
        # 防止无限循环
        if version > 1000:
            raise RuntimeError(f"无法生成文件名，版本号超过限制: {page_slug}")


def _generate_refactor_file_name(output_path: Path, page_slug: str, old_file_name: str) -> str:
    """场景B：基于旧文件名生成新的版本文件名"""
    date_str = datetime.now().strftime('%Y%m%d')

    # 解析旧文件名中的版本号
    old_version = _extract_version_from_file_name(old_file_name)
    new_version = old_version + 1

    # 生成新文件名
    file_name = f"prototype-{date_str}-{page_slug}-v{new_version}.html"

    # 如果文件名已存在，继续递增
    while (output_path / file_name).exists():
        new_version += 1
        file_name = f"prototype-{date_str}-{page_slug}-v{new_version}.html"
        if new_version > 1000:
            raise RuntimeError(f"无法生成文件名，版本号超过限制: {page_slug}")

    return file_name


def _extract_version_from_file_name(file_name: str) -> int:
    """从文件名中提取版本号，如果没有则返回1"""
    import re
    # 匹配 -v{n}.html 或 -v{n} 格式
    match = re.search(r'-v(\d+)(?:\.html)?$', file_name)
    if match:
        return int(match.group(1))
    return 1


if __name__ == '__main__':
    # 示例用法
    example = {
        'page_name': '用户管理',
        'columns': [
            {'title': '用户名', 'dataIndex': 'username'},
            {'title': '邮箱', 'dataIndex': 'email'},
            {'title': '状态', 'dataIndex': 'status', 'render': 'tag'},
            {'title': '创建时间', 'dataIndex': 'createdAt'},
            {'title': '操作', 'dataIndex': 'actions', 'render': 'actions'},
        ],
        'search_fields': [
            {'label': '用户名', 'type': 'input'},
            {'label': '状态', 'type': 'select', 'options': ['启用', '禁用']},
        ],
        'actions': ['新增用户', '批量删除', '导出'],
        'mock_data': [
            {'username': 'admin', 'email': 'admin@example.com', 'status': '启用', 'status_color': 'green', 'createdAt': '2024-03-25'},
            {'username': 'user1', 'email': 'user1@example.com', 'status': '禁用', 'status_color': 'red', 'createdAt': '2024-03-24'},
        ],
        'overview': '本页面用于管理系统用户，支持用户的增删改查、状态管理和批量操作。',
        'sections': [
            {
                'title': '搜索区域',
                'items': [
                    {'label': '搜索按钮', 'desc': '点击后根据输入条件筛选表格数据'},
                    {'label': '重置按钮', 'desc': '清空所有搜索条件，恢复初始列表'},
                    {'label': '筛选字段', 'desc': '支持按用户名、状态、时间范围筛选'},
                ]
            },
            {
                'title': '数据表格',
                'items': [
                    {'label': '列定义', 'desc': '用户名、邮箱、状态、创建时间、操作'},
                    {'label': '排序', 'desc': '支持按创建时间升序/降序排列'},
                    {'label': '分页', 'desc': '默认每页10条，支持10/20/50条切换'},
                ]
            },
        ]
    }

    prototype = PrototypeTemplate.generate_list_page(
        title=example['page_name'],
        columns=example['columns'],
        search_fields=example['search_fields'],
        actions=example['actions'],
        mock_data=example['mock_data']
    )

    description = PrototypeTemplate.generate_description(
        page_name=example['page_name'],
        overview=example['overview'],
        sections=example['sections']
    )

    file_path = save_prototype(
        page_name=example['page_name'],
        output_dir='docs/prototype',
        prototype_content=prototype,
        description_content=description
    )

    print(f"Prototype saved to: {file_path}")
