"""
原型页面生成脚本
根据页面需求生成单个HTML原型文件

用法:
    python generate_page.py --config <json_config_path>
    python generate_page.py --input '{"page_name": "...", "page_type": "...", ...}'
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import re


# Ant Design 配色
COLORS = {
    'primary': '#1677ff',
    'success': '#52c41a',
    'warning': '#faad14',
    'error': '#f5222d',
}


def generate_base_html(title: str, prototype_content: str, description_content: str) -> str:
    """生成基础HTML框架"""
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>原型 - {title}</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/antd/4.24.15/antd.min.css">
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    /* 页面级布局样式 */
    .prototype-container {{ display: flex; height: 100vh; overflow: hidden; }}
    .prototype-left {{ width: 1200px; background: white; overflow: auto; flex-shrink: 0; }}
    .prototype-right {{ flex: 1; background: #f5f5f5; padding: 24px; overflow: auto; }}
  </style>
</head>
<body class="bg-gray-100">
  <div class="prototype-container">
    <!-- 左侧：原型页面（1200px固定宽度） -->
    <div class="prototype-left">
{prototype_content}
    </div>

    <!-- 右侧：交互说明 -->
    <div class="prototype-right">
{description_content}
    </div>
  </div>

  <script>
    // Mock 交互函数
    function mockAction(action, data) {{
      console.log('[Mock]', action, data);
      alert(action + ' 成功（模拟）');
    }}
  </script>
</body>
</html>'''


def generate_list_page(config: Dict) -> str:
    """生成列表页原型"""
    data = config.get('data', {})
    interactions = config.get('interactions', {})
    boundary = config.get('boundary', {})
    page_name = config.get('page_name', '列表页')

    columns = data.get('columns', [])
    buttons = interactions.get('buttons', [])

    # 构建表格列
    th_html = ''
    for col in columns:
        th_html += f'              <th class="ant-table-cell">{col["title"]}</th>\n'

    # 构建表格数据（mock）
    tbody_html = ''
    for i in range(3):
        tbody_html += '            <tr class="ant-table-row">\n'
        for col in columns:
            if col.get('type') == 'tag':
                tag_class = 'ant-tag-green' if i % 2 == 0 else 'ant-tag-red'
                value = f'<span class="ant-tag {tag_class}">{"启用" if i % 2 == 0 else "禁用"}</span>'
            elif col.get('type') == 'actions':
                value = '<a href="#" class="text-blue-500 hover:underline mr-2" onclick="mockAction(\'编辑\')">编辑</a><a href="#" class="text-red-500 hover:underline" onclick="mockAction(\'删除\')">删除</a>'
            else:
                value = f'示例数据{i+1}'
            tbody_html += f'              <td class="ant-table-cell">{value}</td>\n'
        tbody_html += '            </tr>\n'

    # 构建操作按钮
    actions_html = ''
    for btn in buttons:
        btn_class = 'ant-btn-primary' if btn in ['新增', '创建', '添加'] else ''
        actions_html += f'        <button class="ant-btn {btn_class} mr-2" onclick="mockAction(\'{btn}\')">{btn}</button>\n'

    # 构建搜索区域
    search_html = '<div class="flex gap-2">\n'
    for col in columns[:3]:  # 取前3列作为搜索条件
        if col.get('type') != 'actions':
            search_html += f'        <input class="ant-input" placeholder="{col["title"]}" style="width: 200px;">\n'
    search_html += '        <button class="ant-btn ant-btn-primary" onclick="mockAction(\'搜索\')">搜索</button>\n'
    search_html += '        <button class="ant-btn" onclick="mockAction(\'重置\')">重置</button>\n'
    search_html += '      </div>'

    return f'''<div class="flex flex-col min-h-full">
  <!-- 顶栏 -->
  <header class="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6">
    <div class="flex items-center gap-4">
      <div class="w-8 h-8 bg-blue-500 rounded flex items-center justify-center text-white font-bold">S</div>
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
        <a href="#" class="flex items-center gap-3 px-4 py-3 rounded bg-blue-600 text-white">
          <span>📋</span>
          <span>{page_name}</span>
        </a>
      </nav>
    </aside>

    <!-- 主内容 -->
    <main class="flex-1 overflow-auto bg-gray-50 p-6">
      <!-- 面包屑 -->
      <div class="mb-4 text-sm text-gray-500">
        <span>首页</span>
        <span class="mx-2">/</span>
        <span>{page_name}</span>
      </div>

      <!-- 搜索区域 -->
      <div class="bg-white p-4 rounded mb-4">
{search_html}
      </div>

      <!-- 操作栏 -->
      <div class="bg-white p-4 rounded mb-4 flex justify-between items-center">
        <div>{actions_html}</div>
      </div>

      <!-- 表格 -->
      <div class="bg-white rounded">
        <div class="ant-table-wrapper">
          <div class="ant-table">
            <div class="ant-table-container">
              <div class="ant-table-content">
                <table style="width: 100%;">
                  <thead class="ant-table-thead">
                    <tr>
{th_html}                    </tr>
                  </thead>
                  <tbody class="ant-table-tbody">
{tbody_html}                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <div class="p-4 border-t border-gray-200 flex justify-end items-center gap-4">
          <span class="text-sm text-gray-500">共 100 条</span>
          <div class="flex gap-1">
            <button class="px-3 py-1 border rounded hover:border-blue-500 disabled:opacity-50" disabled>&lt;</button>
            <button class="px-3 py-1 border rounded bg-blue-500 text-white">1</button>
            <button class="px-3 py-1 border rounded hover:border-blue-500">2</button>
            <button class="px-3 py-1 border rounded hover:border-blue-500">&gt;</button>
          </div>
        </div>
      </div>
    </main>
  </div>
</div>'''


def generate_form_page(config: Dict) -> str:
    """生成表单页原型"""
    data = config.get('data', {})
    page_name = config.get('page_name', '表单页')
    fields = data.get('fields', [])

    # 构建表单字段
    fields_html = ''
    for field in fields:
        required_mark = '<span class="text-red-500">*</span>' if field.get('required') else ''
        if field.get('type') == 'select':
            options = ''.join([f'<option>{opt}</option>' for opt in field.get('options', ['选项1', '选项2'])])
            input_html = f'<select class="ant-input"><option>请选择</option>{options}</select>'
        elif field.get('type') == 'textarea':
            input_html = '<textarea class="ant-input" rows="3" placeholder="请输入{field["label"]}"></textarea>'
        else:
            input_html = f'<input class="ant-input" placeholder="请输入{field["label"]}">'

        fields_html += f'''
        <div class="ant-row ant-form-item">
          <div class="ant-col ant-form-item-label" style="width: 120px;">
            <label>{field["label"]}{required_mark}</label>
          </div>
          <div class="ant-col ant-form-item-control">
            {input_html}
          </div>
        </div>'''

    return f'''<div class="flex flex-col min-h-full">
  <!-- 顶栏 -->
  <header class="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6">
    <div class="flex items-center gap-4">
      <div class="w-8 h-8 bg-blue-500 rounded flex items-center justify-center text-white font-bold">S</div>
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
        <a href="#" class="flex items-center gap-3 px-4 py-3 rounded bg-blue-600 text-white">
          <span>📝</span>
          <span>{page_name}</span>
        </a>
      </nav>
    </aside>

    <!-- 主内容 -->
    <main class="flex-1 overflow-auto bg-gray-50 p-6">
      <!-- 面包屑 -->
      <div class="mb-4 text-sm text-gray-500">
        <span>首页</span>
        <span class="mx-2">/</span>
        <span>{page_name}</span>
      </div>

      <!-- 表单卡片 -->
      <div class="ant-card bg-white rounded p-6 max-w-3xl">
        <div class="ant-card-head mb-4">
          <div class="ant-card-head-title text-lg font-semibold">{page_name}</div>
        </div>
        <div class="ant-card-body">
          <form class="ant-form">
{fields_html}
            <div class="ant-form-item mt-6">
              <div class="ant-col ant-form-item-control" style="margin-left: 120px;">
                <button type="button" class="ant-btn ant-btn-primary mr-2" onclick="mockAction('提交')">提交</button>
                <button type="button" class="ant-btn" onclick="mockAction('取消')">取消</button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </main>
  </div>
</div>'''


def generate_detail_page(config: Dict) -> str:
    """生成详情页原型"""
    data = config.get('data', {})
    page_name = config.get('page_name', '详情页')
    groups = data.get('groups', [])

    # 构建详情分组
    groups_html = ''
    for group in groups:
        fields_html = ''
        for field in group.get('fields', []):
            fields_html += f'''
            <div class="ant-descriptions-item flex py-2">
              <span class="text-gray-500 w-32">{field}:</span>
              <span class="text-gray-800">示例{field}值</span>
            </div>'''

        groups_html += f'''
        <div class="ant-card bg-white rounded p-4 mb-4">
          <div class="ant-card-head mb-3 border-b pb-2">
            <div class="ant-card-head-title font-medium">{group.get('title', '分组')}</div>
          </div>
          <div class="ant-card-body">
{fields_html}
          </div>
        </div>'''

    return f'''<div class="flex flex-col min-h-full">
  <!-- 顶栏 -->
  <header class="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6">
    <div class="flex items-center gap-4">
      <div class="w-8 h-8 bg-blue-500 rounded flex items-center justify-center text-white font-bold">S</div>
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
        <a href="#" class="flex items-center gap-3 px-4 py-3 rounded bg-blue-600 text-white">
          <span>📄</span>
          <span>{page_name}</span>
        </a>
      </nav>
    </aside>

    <!-- 主内容 -->
    <main class="flex-1 overflow-auto bg-gray-50 p-6">
      <!-- 面包屑 -->
      <div class="mb-4 text-sm text-gray-500">
        <span>首页</span>
        <span class="mx-2">/</span>
        <span>{page_name}</span>
      </div>

      <!-- 操作栏 -->
      <div class="mb-4">
        <button class="ant-btn ant-btn-primary mr-2" onclick="mockAction('编辑')">编辑</button>
        <button class="ant-btn" onclick="mockAction('返回')">返回</button>
      </div>

      <!-- 详情内容 -->
{groups_html}
    </main>
  </div>
</div>'''


def generate_description(config: Dict) -> str:
    """生成右侧说明文档"""
    page_name = config.get('page_name', '页面')
    clarification = config.get('clarification', {})
    interactions = clarification.get('interactions', {})
    boundary = clarification.get('boundary', {})
    layout = clarification.get('layout', {})
    data = clarification.get('data', {})

    # 构建交互说明
    interactions_html = ''
    if interactions.get('buttons'):
        interactions_html += '<h4 class="font-medium mb-2">操作按钮</h4><ul class="list-disc pl-5 mb-4 space-y-1">'
        for btn in interactions['buttons']:
            interactions_html += f'<li>{btn}: 点击后触发相应操作</li>'
        interactions_html += '</ul>'

    if interactions.get('modal_type'):
        interactions_html += f'<p class="mb-2"><span class="font-medium">编辑/新增方式:</span> {interactions["modal_type"]}</p>'

    # 构建边界说明
    boundary_html = '<ul class="list-disc pl-5 space-y-1">'
    if boundary.get('empty_state'):
        boundary_html += f'<li><span class="font-medium">空数据:</span> {boundary["empty_state"]}</li>'
    if boundary.get('loading_state'):
        boundary_html += f'<li><span class="font-medium">加载中:</span> {boundary["loading_state"]}</li>'
    if boundary.get('error_state'):
        boundary_html += f'<li><span class="font-medium">错误:</span> {boundary["error_state"]}</li>'
    boundary_html += '</ul>'

    # 布局说明
    layout_html = f'<p class="mb-2"><span class="font-medium">布局类型:</span> {layout.get("type", "顶栏+侧边栏+内容区")}</p>'
    if layout.get('modules'):
        layout_html += '<p class="font-medium">模块划分:</p><ul class="list-disc pl-5 mb-4">'
        for mod in layout['modules']:
            layout_html += f'<li>{mod}</li>'
        layout_html += '</ul>'

    return f'''<div class="max-w-2xl">
  <div class="mb-6">
    <h2 class="text-xl font-bold text-gray-800 mb-1">{page_name} 原型说明</h2>
    <p class="text-sm text-gray-500">生成日期: {datetime.now().strftime('%Y-%m-%d')}</p>
  </div>

  <!-- 页面概述 -->
  <div class="mb-6">
    <h3 class="text-base font-semibold text-gray-800 mb-2 pb-2 border-b border-gray-200">1. 页面概述</h3>
    <p class="text-gray-600 text-sm leading-relaxed">本页面为{page_name}原型，展示页面布局、组件和交互逻辑。</p>
  </div>

  <!-- 布局说明 -->
  <div class="mb-6">
    <h3 class="text-base font-semibold text-gray-800 mb-2 pb-2 border-b border-gray-200">2. 布局结构</h3>
    {layout_html}
  </div>

  <!-- 交互说明 -->
  <div class="mb-6">
    <h3 class="text-base font-semibold text-gray-800 mb-2 pb-2 border-b border-gray-200">3. 交互逻辑</h3>
    {interactions_html if interactions_html else '<p class="text-gray-600 text-sm">标准交互逻辑</p>'}
  </div>

  <!-- 边界场景 -->
  <div class="mb-6">
    <h3 class="text-base font-semibold text-gray-800 mb-2 pb-2 border-b border-gray-200">4. 边界场景</h3>
    {boundary_html}
  </div>
</div>'''


def extract_version_from_file_name(file_name: str) -> int:
    """从文件名中提取版本号，如果没有则返回1"""
    match = re.search(r'-v(\d+)(?:\.html)?$', file_name)
    if match:
        return int(match.group(1))
    return 1


def generate_file_name(output_dir: Path, page_slug: str, scenario: str, old_file_name: Optional[str]) -> str:
    """生成文件名"""
    date_str = datetime.now().strftime('%Y%m%d')

    if scenario == 'refactor' and old_file_name:
        # 场景B：基于旧文件版本递增
        old_version = extract_version_from_file_name(old_file_name)
        new_version = old_version + 1
        file_name = f"prototype-{date_str}-{page_slug}-v{new_version}.html"
        # 如果文件名已存在，继续递增
        while (output_dir / file_name).exists():
            new_version += 1
            file_name = f"prototype-{date_str}-{page_slug}-v{new_version}.html"
    else:
        # 场景A：新原型
        file_name = f"prototype-{date_str}-{page_slug}.html"
        if (output_dir / file_name).exists():
            version = 2
            while (output_dir / f"prototype-{date_str}-{page_slug}-v{version}.html").exists():
                version += 1
            file_name = f"prototype-{date_str}-{page_slug}-v{version}.html"

    return file_name


def generate_page(config: Dict) -> Dict:
    """生成单个页面原型

    Returns:
        {
            "file_path": "...",
            "file_name": "...",
            "status": "success|error",
            "message": "..."
        }
    """
    try:
        page_name = config.get('page_name')
        page_type = config.get('page_type', 'list')
        output_path_str = config.get('output_path', 'docs/prototype')
        scenario = config.get('scenario', 'new')
        old_prototype_code = config.get('old_prototype_code')

        if not page_name:
            return {"status": "error", "message": "缺少 page_name 参数"}

        output_dir = Path(output_path_str)
        output_dir.mkdir(parents=True, exist_ok=True)

        # 生成页面简称
        page_slug = page_name.lower().replace(' ', '-').replace('_', '-')

        # 生成文件名
        file_name = generate_file_name(output_dir, page_slug, scenario, config.get('old_file_name'))

        # 根据页面类型生成原型内容
        page_generators = {
            'list': generate_list_page,
            'form': generate_form_page,
            'detail': generate_detail_page,
        }

        generator = page_generators.get(page_type, generate_list_page)
        prototype_content = generator(config)

        # 生成说明文档
        description_content = generate_description(config)

        # 生成完整HTML
        full_html = generate_base_html(page_name, prototype_content, description_content)

        # 保存文件
        file_path = output_dir / file_name
        file_path.write_text(full_html, encoding='utf-8')

        return {
            "file_path": str(file_path),
            "file_name": file_name,
            "status": "success",
            "message": "生成成功" if scenario == 'new' else f"改造成功，已生成新版本",
            "page_info": {
                "name": page_name,
                "type": page_type,
                "scenario": scenario,
                "version": extract_version_from_file_name(file_name)
            }
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "error": {"type": "generation_error", "detail": str(e)}
        }


def main():
    parser = argparse.ArgumentParser(description='生成原型页面HTML')
    parser.add_argument('--config', '-c', help='JSON配置文件路径')
    parser.add_argument('--input', '-i', help='JSON格式的输入参数')
    parser.add_argument('--output', '-o', help='输出结果到文件')

    args = parser.parse_args()

    # 读取配置
    if args.config:
        config = json.loads(Path(args.config).read_text(encoding='utf-8'))
    elif args.input:
        config = json.loads(args.input)
    else:
        # 从stdin读取
        config = json.loads(sys.stdin.read())

    # 生成页面
    result = generate_page(config)

    # 输出结果
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding='utf-8')
    else:
        print(output)

    # 返回退出码
    sys.exit(0 if result['status'] == 'success' else 1)


if __name__ == '__main__':
    main()
