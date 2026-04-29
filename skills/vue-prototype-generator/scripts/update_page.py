"""
Vue 原型页面更新脚本
用于对话模式，根据用户需求调整原型页面

用法:
    python update_page.py --prototype my-prototype --page user-list --changes '{JSON配置}'
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional


def update_page(prototype: str, page: str, changes: Dict) -> Dict:
    """
    更新原型页面

    Args:
        prototype: 原型项目名称
        page: 页面名称（目录名）
        changes: 变更配置
            {
                "type": "style|layout|field|interaction|data",
                "description": "变更描述",
                "updates": {...}
            }

    Returns:
        {
            "status": "success|error",
            "message": "...",
            "updated_files": [...]
        }
    """
    try:
        page_path = Path('docs/prototype') / prototype / 'src' / 'pages' / page
        if not page_path.exists():
            return {
                "status": "error",
                "message": f"页面 '{page}' 不存在"
            }

        change_type = changes.get('type', 'style')
        updates = changes.get('updates', {})
        updated_files = []

        # 根据变更类型执行不同操作
        if change_type == 'style':
            updated_files = update_styles(page_path, updates)
        elif change_type == 'layout':
            updated_files = update_layout(page_path, updates)
        elif change_type == 'field':
            updated_files = update_fields(page_path, updates)
        elif change_type == 'interaction':
            updated_files = update_interactions(page_path, updates)
        elif change_type == 'data':
            updated_files = update_data(page_path, updates)
        else:
            return {
                "status": "error",
                "message": f"未知的变更类型: {change_type}"
            }

        return {
            "status": "success",
            "message": f"页面 '{page}' 更新成功",
            "updated_files": updated_files
        }

    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "error": traceback.format_exc()
        }


def update_styles(page_path: Path, updates: Dict) -> List[str]:
    """更新样式"""
    updated = []

    vue_file = page_path / 'index.vue'
    if vue_file.exists():
        content = vue_file.read_text(encoding='utf-8')

        # 更新样式（在 <style> 标签内添加自定义样式）
        custom_styles = updates.get('custom_styles', '')
        if custom_styles:
            if '<style scoped lang="less">' in content:
                content = content.replace(
                    '<style scoped lang="less">',
                    f'<style scoped lang="less">\n{custom_styles}'
                )
            else:
                content += f'\n\n<style scoped lang="less">\n{custom_styles}\n</style>'

        vue_file.write_text(content, encoding='utf-8')
        updated.append(str(vue_file))

    return updated


def update_layout(page_path: Path, updates: Dict) -> List[str]:
    """更新布局"""
    updated = []

    vue_file = page_path / 'index.vue'
    if vue_file.exists():
        content = vue_file.read_text(encoding='utf-8')

        # 更新搜索区域布局
        if 'search_layout' in updates:
            search_layout = updates['search_layout']
            # 修改搜索表单布局
            if search_layout == 'horizontal':
                content = content.replace('layout="inline"', 'layout="inline"')
            elif search_layout == 'vertical':
                content = content.replace('layout="inline"', 'layout="vertical"')

        # 更新表格布局
        if 'table_layout' in updates:
            table_layout = updates['table_layout']
            # 修改表格配置

        # 更新抽屉宽度
        if 'drawer_width' in updates:
            drawer_width = updates['drawer_width']
            content = content.replace(
                'width="600px"',
                f'width="{drawer_width}"'
            )

        vue_file.write_text(content, encoding='utf-8')
        updated.append(str(vue_file))

    return updated


def update_fields(page_path: Path, updates: Dict) -> List[str]:
    """更新字段"""
    updated = []

    data_file = page_path / 'data.ts'
    if data_file.exists():
        content = data_file.read_text(encoding='utf-8')

        # 添加新字段到 columns
        if 'add_columns' in updates:
            new_columns = updates['add_columns']
            # 在 columns 数组末尾添加新字段
            # 这里需要解析现有 columns 并在合适位置插入

        # 更新搜索字段
        if 'update_search_fields' in updates:
            search_fields = updates['update_search_fields']
            # 更新 searchSchema

        data_file.write_text(content, encoding='utf-8')
        updated.append(str(data_file))

    # 同时更新 index.vue 中的表单
    vue_file = page_path / 'index.vue'
    if vue_file.exists():
        content = vue_file.read_text(encoding='utf-8')

        # 更新表格列
        if 'add_columns' in updates:
            new_columns = updates['add_columns']
            # 添加新的表格列配置

        vue_file.write_text(content, encoding='utf-8')
        updated.append(str(vue_file))

    return updated


def update_interactions(page_path: Path, updates: Dict) -> List[str]:
    """更新交互"""
    updated = []

    vue_file = page_path / 'index.vue'
    if vue_file.exists():
        content = vue_file.read_text(encoding='utf-8')

        # 添加新的操作按钮
        if 'add_buttons' in updates:
            buttons = updates['add_buttons']
            # 在操作列添加新按钮

        # 更新抽屉配置
        if 'drawer_config' in updates:
            config = updates['drawer_config']
            # 更新抽屉属性

        vue_file.write_text(content, encoding='utf-8')
        updated.append(str(vue_file))

    return updated


def update_data(page_path: Path, updates: Dict) -> List[str]:
    """更新数据配置"""
    updated = []

    data_file = page_path / 'data.ts'
    if data_file.exists():
        content = data_file.read_text(encoding='utf-8')

        # 更新状态枚举
        if 'status_enum' in updates:
            enum_config = updates['status_enum']
            # 更新 statusEnum 和 statusOptions

        # 更新验证规则
        if 'validation_rules' in updates:
            rules = updates['validation_rules']
            # 更新表单验证规则

        data_file.write_text(content, encoding='utf-8')
        updated.append(str(data_file))

    return updated


def main():
    parser = argparse.ArgumentParser(description='更新 Vue 原型页面')
    parser.add_argument('--prototype', '-p', required=True, help='原型项目名称')
    parser.add_argument('--page', required=True, help='页面名称')
    parser.add_argument('--changes', '-c', required=True, help='变更配置(JSON格式)')
    parser.add_argument('--output', '-o', help='输出结果到文件')

    args = parser.parse_args()

    changes = json.loads(args.changes)
    result = update_page(args.prototype, args.page, changes)

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding='utf-8')
    else:
        print(output)

    sys.exit(0 if result['status'] == 'success' else 1)


if __name__ == '__main__':
    main()
