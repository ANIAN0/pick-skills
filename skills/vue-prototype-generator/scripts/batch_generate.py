"""
Vue 原型批量生成脚本
根据配置批量生成多个 HTML 预览文件

用法:
    python batch_generate.py --config pages.json
    python batch_generate.py --input '[{"page_name": "..."}, ...]'

pages.json 格式:
{
  "output_path": ".dev/prototype",
  "pages": [
    {
      "page_name": "用户列表",
      "page_type": "list",
      "data": {...},
      "interactions": {...}
    },
    {...}
  ]
}
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List

# 导入 generate_page 模块
sys.path.insert(0, str(Path(__file__).parent))
from generate_page import generate_page


def batch_generate(config_path: str = None, config_data: Dict = None) -> Dict:
    """批量生成页面原型

    Args:
        config_path: JSON配置文件路径
        config_data: 直接传入的配置数据

    Returns:
        {
            "status": "success|partial|error",
            "message": "...",
            "results": [...],
            "success_count": N,
            "fail_count": N
        }
    """
    try:
        # 读取配置
        if config_path:
            config = json.loads(Path(config_path).read_text(encoding='utf-8'))
        elif config_data:
            config = config_data
        else:
            # 从stdin读取
            config = json.loads(sys.stdin.read())

        pages = config.get('pages', [])
        output_path = config.get('output_path', '.dev/prototype')

        if not pages:
            return {
                "status": "error",
                "message": "配置中没有页面定义",
                "results": [],
                "success_count": 0,
                "fail_count": 0
            }

        results = []
        success_count = 0
        fail_count = 0

        # 串行生成（避免文件冲突）
        for page_config in pages:
            # 注入公共配置
            page_config['output_path'] = page_config.get('output_path', output_path)

            result = generate_page(page_config)
            results.append(result)

            if result['status'] == 'success':
                success_count += 1
                print(f"✓ 生成成功: {result['file_name']}")
            else:
                fail_count += 1
                print(f"✗ 生成失败: {page_config.get('page_name', '未知')} - {result['message']}")

        # 确定整体状态
        if success_count == len(pages):
            status = "success"
            message = f"全部 {success_count} 个页面生成成功"
        elif success_count > 0:
            status = "partial"
            message = f"部分生成成功: {success_count} 成功, {fail_count} 失败"
        else:
            status = "error"
            message = f"全部生成失败: {fail_count} 个页面"

        return {
            "status": status,
            "message": message,
            "results": results,
            "success_count": success_count,
            "fail_count": fail_count
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"批量生成失败: {str(e)}",
            "results": [],
            "success_count": 0,
            "fail_count": 0
        }


def main():
    parser = argparse.ArgumentParser(description='批量生成 Vue 原型 HTML 页面')
    parser.add_argument('--config', '-c', help='JSON配置文件路径')
    parser.add_argument('--input', '-i', help='JSON格式的输入参数')
    parser.add_argument('--output', '-o', help='输出结果到文件')

    args = parser.parse_args()

    # 执行批量生成
    if args.config:
        result = batch_generate(config_path=args.config)
    elif args.input:
        result = batch_generate(config_data=json.loads(args.input))
    else:
        result = batch_generate()

    # 输出结果
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding='utf-8')
    else:
        print(output)

    # 返回退出码
    sys.exit(0 if result['status'] in ['success', 'partial'] else 1)


if __name__ == '__main__':
    main()
