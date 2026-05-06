#!/usr/bin/env python3
"""
clone_page.py - 从 .vue 文件提取组件结构，输出 JSON 供原型生成使用。

用法：
  python clone_page.py --vue-file "path/to/page.vue" [--data-file "path/to/data.ts"] [--output ".dev/prototype/analysis.json"]

功能：
  1. 解析 .vue SFC 文件，提取 template、script、style 部分
  2. 分析 template 中的组件结构（tl 布局、表格、筛选、抽屉等）
  3. 解析 data.ts 中的 columns、searchSchema、状态枚举
  4. 输出结构化 JSON
"""

import argparse
import json
import os
import re
import sys


def read_file(path):
    """读取文件内容"""
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def parse_vue_sfc(content):
    """解析 Vue SFC，提取 template、script、style 部分"""
    result = {'template': '', 'script': '', 'styles': []}

    # 提取 template
    template_match = re.search(r'<template>(.*?)</template>', content, re.DOTALL)
    if template_match:
        result['template'] = template_match.group(1).strip()

    # 提取 script
    script_match = re.search(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
    if script_match:
        result['script'] = script_match.group(1).strip()

    # 提取 style
    style_matches = re.findall(r'<style[^>]*>(.*?)</style>', content, re.DOTALL)
    result['styles'] = [s.strip() for s in style_matches]

    return result


def extract_template_components(template):
    """从 template 中提取组件结构"""
    components = {
        'has_tl_layout': bool(re.search(r'<tl[>\s]', template)),
        'has_tl_filter': bool(re.search(r'<tl-filter', template)),
        'has_tl_table': bool(re.search(r'<tl-table', template)),
        'has_tl_drawer': bool(re.search(r'<tl-drawer', template)),
        'has_yc_form': bool(re.search(r'<yc-form', template)),
        'has_yc_status': bool(re.search(r'<yc-status', template)),
        'has_action_group': bool(re.search(r'<action-group', template)),
        'has_a_table': bool(re.search(r'<a-table', template)),
        'has_modal': bool(re.search(r'<a-modal|<tl-modal', template)),
    }

    # 提取 drawer 属性
    drawer_attrs = {}
    drawer_match = re.search(r'<tl-drawer([^>]*)>', template)
    if drawer_match:
        attrs_str = drawer_match.group(1)
        width_match = re.search(r'width="([^"]*)"', attrs_str)
        if width_match:
            drawer_attrs['width'] = width_match.group(1)

    # 提取 action-group 中的按钮
    action_buttons = []
    ag_matches = re.findall(r'<a-button([^>]*)>(.*?)</a-button>', template, re.DOTALL)
    for attrs, btn_text in ag_matches:
        clean_text = re.sub(r'<[^>]+>', '', btn_text).strip()
        if clean_text:
            btn_type = 'danger' if 'danger' in attrs else 'link'
            action_buttons.append({
                'text': clean_text,
                'type': btn_type
            })

    # 提取搜索按钮区域
    search_buttons = []
    filter_section = re.search(r'<tl-filter-left>(.*?)</tl-filter-left>', template, re.DOTALL)
    if filter_section:
        btn_matches = re.findall(r'<a-button([^>]*)>(.*?)</a-button>', filter_section.group(1), re.DOTALL)
        for attrs, text in btn_matches:
            clean_text = re.sub(r'<[^>]+>', '', text).strip()
            btn_type = 'primary' if 'type="primary"' in attrs else 'default'
            click_handler = re.search(r'@click="([^"]*)"', attrs)
            search_buttons.append({
                'text': clean_text,
                'type': btn_type,
                'handler': click_handler.group(1) if click_handler else None
            })

    # 提取 bodyCell 模板中的列渲染逻辑
    body_cell_blocks = re.findall(r'<template\s+#bodyCell[^>]*>(.*?)</template>', template, re.DOTALL)

    return {
        **components,
        'drawer_attrs': drawer_attrs,
        'action_buttons': action_buttons,
        'search_buttons': search_buttons,
        'body_cell_blocks': body_cell_blocks,
    }


def extract_script_data(script):
    """从 script 中提取数据结构信息"""
    result = {
        'imports': [],
        'page_name': None,
        'in_params': {},
        'api_methods': [],
        'drawer_modes': [],
    }

    # 提取 import
    import_matches = re.findall(r"import\s+\{([^}]+)\}\s+from\s+'([^']+)'", script)
    for items, source in import_matches:
        for item in items.split(','):
            result['imports'].append({'name': item.strip(), 'from': source})

    # 提取 PAGE_NAME
    page_name_match = re.search(r"PAGE_NAME\s*=\s*'([^']+)'", script)
    if page_name_match:
        result['page_name'] = page_name_match.group(1)

    # 提取 inParams 结构
    in_params_match = re.search(r'(?:const|let)\s+\w+\s*=\s*reactive(?:<[^>]+>)?\(\{([^}]+)\}', script)
    if in_params_match:
        params_str = in_params_match.group(1)
        for line in params_str.split(','):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                result['in_params'][key.strip()] = value.strip()

    # 提取 drawer 模式
    drawer_open_matches = re.findall(r"drawer\.open\('(\w+)'", script)
    result['drawer_modes'] = list(set(drawer_open_matches))

    # 提取 API 方法
    api_matches = re.findall(r"await\s+(\w+)\(", script)
    result['api_methods'] = list(set(api_matches))

    return result


def extract_data_ts(content):
    """解析 data.ts 文件，提取 columns、searchSchema、枚举"""
    result = {
        'columns': [],
        'search_schema': [],
        'enums': {},
    }

    if not content:
        return result

    # 提取 columns 数组
    columns_match = re.search(r'(?:export\s+const\s+columns\s*[:=]\s*)(?:\w+\s*)?(?:\[|=\s*\[)(.*?)\]', content, re.DOTALL)
    if columns_match:
        cols_str = columns_match.group(1)
        # 提取每个 column 对象
        col_objects = re.findall(r'\{([^}]+)\}', cols_str)
        for col_str in col_objects:
            col = {}
            title_match = re.search(r'title:\s*["\']([^"\']+)["\']', col_str)
            data_index_match = re.search(r'dataIndex:\s*["\']([^"\']+)["\']', col_str)
            width_match = re.search(r'width:\s*["\']?(\d+px?)["\']?', col_str)
            align_match = re.search(r'align:\s*["\']([^"\']+)["\']', col_str)
            fixed_match = re.search(r'fixed:\s*["\']([^"\']+)["\']', col_str)

            if title_match:
                col['title'] = title_match.group(1)
            if data_index_match:
                col['dataIndex'] = data_index_match.group(1)
            if width_match:
                col['width'] = width_match.group(1)
            if align_match:
                col['align'] = align_match.group(1)
            if fixed_match:
                col['fixed'] = fixed_match.group(1)

            if col:
                result['columns'].append(col)

    # 提取 searchSchema
    schema_match = re.search(r'(?:export\s+const\s+searchSchema\s*[:=]\s*)(?:\w+\s*)?\[([\s\S]*?)\]', content)
    if schema_match:
        schema_str = schema_match.group(1)
        field_objects = re.findall(r'\{([^}]+)\}', schema_str)
        for field_str in field_objects:
            field = {}
            field_match = re.search(r'field:\s*["\']([^"\']+)["\']', field_str)
            label_match = re.search(r'label:\s*["\']([^"\']+)["\']', field_str)
            component_match = re.search(r'component:\s*["\']([^"\']+)["\']', field_str)
            placeholder_match = re.search(r'placeholder:\s*["\']([^"\']+)["\']', field_str)

            if field_match:
                field['field'] = field_match.group(1)
            if label_match:
                field['label'] = label_match.group(1)
            if component_match:
                field['component'] = component_match.group(1)
            if placeholder_match:
                field['placeholder'] = placeholder_match.group(1)

            if field:
                result['search_schema'].append(field)

    # 提取枚举定义
    enum_matches = re.findall(r'(?:export\s+)?(?:const|enum)\s+(\w+)\s*[=:]\s*\{([^}]+)\}', content)
    for name, values_str in enum_matches:
        enum_values = {}
        for item in values_str.split(','):
            item = item.strip()
            if '=' in item:
                key, value = item.split('=', 1)
                enum_values[key.strip()] = value.strip().strip("'\"")
        if enum_values:
            result['enums'][name] = enum_values

    return result


def find_associated_files(vue_path):
    """查找与 .vue 文件关联的 data.ts 和子组件"""
    directory = os.path.dirname(vue_path)
    associated = {'data_ts': None, 'components': []}

    # 查找 data.ts
    data_file = os.path.join(directory, 'data.ts')
    if os.path.exists(data_file):
        associated['data_ts'] = data_file

    # 查找 components/ 目录下的子组件
    components_dir = os.path.join(directory, 'components')
    if os.path.isdir(components_dir):
        for f in os.listdir(components_dir):
            if f.endswith('.vue'):
                associated['components'].append(os.path.join(components_dir, f))

    return associated


def analyze_vue(vue_path, data_file=None):
    """分析 .vue 文件，输出结构化 JSON"""
    content = read_file(vue_path)
    if not content:
        return {'error': f'文件不存在: {vue_path}'}

    # 解析 SFC
    sfc = parse_vue_sfc(content)

    # 提取组件结构
    template_info = extract_template_components(sfc['template'])

    # 提取脚本数据
    script_info = extract_script_data(sfc['script'])

    # 查找关联文件
    associated = find_associated_files(vue_path)

    # 解析 data.ts
    data_ts_content = None
    data_file_path = data_file or associated['data_ts']
    if data_file_path:
        data_ts_content = read_file(data_file_path)

    data_info = extract_data_ts(data_ts_content)

    # 解析子组件（EditForm 等）
    sub_components = {}
    for comp_path in associated['components']:
        comp_content = read_file(comp_path)
        if comp_content:
            comp_sfc = parse_vue_sfc(comp_content)
            comp_name = os.path.splitext(os.path.basename(comp_path))[0]
            sub_components[comp_name] = {
                'template': comp_sfc['template'][:2000],  # 限制长度
                'has_form': bool(re.search(r'<a-form', comp_sfc['template'])),
                'form_fields': extract_form_fields(comp_sfc['template']),
            }

    return {
        'source_file': vue_path,
        'page_type': 'list' if template_info['has_a_table'] else 'form' if template_info.get('has_form') else 'detail',
        'template_components': template_info,
        'script_data': script_info,
        'data_config': data_info,
        'sub_components': sub_components,
        'associated_files': {
            'data_ts': data_file_path,
            'components': associated['components'],
        }
    }


def extract_form_fields(template):
    """从表单模板中提取字段"""
    fields = []
    # 匹配 a-form-item
    form_items = re.findall(r'<a-form-item[^>]*>(.*?)</a-form-item>', template, re.DOTALL)
    for item in form_items:
        field = {}
        label_match = re.search(r'label="([^"]*)"', item)
        name_match = re.search(r'name="([^"]*)"', item)
        required = 'required' in item or '*必填' in item

        if label_match:
            field['label'] = label_match.group(1)
        if name_match:
            field['name'] = name_match.group(1)
        field['required'] = required

        # 识别输入类型
        if '<a-input' in item:
            field['type'] = 'input'
        elif '<a-textarea' in item:
            field['type'] = 'textarea'
        elif '<a-select' in item:
            field['type'] = 'select'
        elif '<a-tree-select' in item:
            field['type'] = 'tree-select'
        elif '<a-input-number' in item:
            field['type'] = 'number'
        elif '<a-switch' in item:
            field['type'] = 'switch'
        elif '<a-radio' in item:
            field['type'] = 'radio'
        elif '<a-date-picker' in item:
            field['type'] = 'date'
        else:
            field['type'] = 'input'

        # 提取 placeholder
        placeholder_match = re.search(r'placeholder="([^"]*)"', item)
        if placeholder_match:
            field['placeholder'] = placeholder_match.group(1)

        if field:
            fields.append(field)

    return fields


def main():
    parser = argparse.ArgumentParser(description='分析 .vue 文件结构')
    parser.add_argument('--vue-file', required=True, help='.vue 文件路径')
    parser.add_argument('--data-file', help='data.ts 文件路径（可选，自动查找）')
    parser.add_argument('--output', help='输出 JSON 文件路径（可选，默认输出到控制台）')
    args = parser.parse_args()

    result = analyze_vue(args.vue_file, args.data_file)

    output_json = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else '.', exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_json)
        print(f"分析结果已保存到: {args.output}")
    else:
        print(output_json)


if __name__ == '__main__':
    main()
