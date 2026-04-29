"""
Vue 原型批量生成脚本
根据配置批量生成多个页面原型

用法:
    python batch_generate.py --config pages.json
    python batch_generate.py --input '{"prototype_name": "xxx", "pages": [...]}'

pages.json 格式:
{
  "prototype_name": "user-prototype",
  "output_path": "docs/prototype",
  "pages": [
    {
      "page_name": "用户列表",
      "page_type": "list",
      "clarification": {...}
    },
    {...}
  ]
}
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List


def batch_generate(config_data: Dict) -> Dict:
    """
    批量生成页面原型

    Args:
        config_data: 配置数据
            {
                "prototype_name": "原型名称",
                "output_path": "输出目录",
                "pages": [页面配置列表]
            }

    Returns:
        {
            "status": "success|partial|error",
            "message": "...",
            "results": [...],
            "prototype_path": "...",
            "next_steps": [...]
        }
    """
    try:
        prototype_name = config_data.get('prototype_name', 'default-prototype')
        output_path = config_data.get('output_path', 'docs/prototype')
        pages = config_data.get('pages', [])

        if not pages:
            return {
                "status": "error",
                "message": "配置中没有页面定义",
                "results": []
            }

        # 第一步：初始化原型项目（如果不存在）
        prototype_dir = Path(output_path) / prototype_name
        if not prototype_dir.exists():
            print(f"🚀 初始化原型项目: {prototype_name}")
            init_result = subprocess.run(
                [
                    sys.executable,
                    Path(__file__).parent / 'init_prototype.py',
                    '--name', prototype_name,
                    '--output', output_path
                ],
                capture_output=True,
                text=True
            )
            if init_result.returncode != 0:
                return {
                    "status": "error",
                    "message": f"初始化原型项目失败: {init_result.stderr}",
                    "results": []
                }
            print(f"✅ 原型项目初始化成功")

        # 第二步：批量生成页面
        results = []
        success_count = 0
        fail_count = 0

        print(f"\n📄 开始生成 {len(pages)} 个页面...")

        for i, page_config in enumerate(pages, 1):
            page_name = page_config.get('page_name', f'页面{i}')
            print(f"\n[{i}/{len(pages)}] 生成页面: {page_name}")

            # 调用 generate_page.py
            gen_result = subprocess.run(
                [
                    sys.executable,
                    Path(__file__).parent / 'generate_page.py',
                    '--input', json.dumps(page_config, ensure_ascii=False),
                    '--prototype', prototype_name
                ],
                capture_output=True,
                text=True
            )

            try:
                result = json.loads(gen_result.stdout)
                results.append(result)

                if result.get('status') == 'success':
                    success_count += 1
                    print(f"✅ 生成成功: {page_name}")
                else:
                    fail_count += 1
                    print(f"❌ 生成失败: {page_name} - {result.get('message')}")
            except json.JSONDecodeError:
                fail_count += 1
                print(f"❌ 生成失败: {page_name} - 解析结果失败")
                print(f"   输出: {gen_result.stdout}")
                print(f"   错误: {gen_result.stderr}")

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

        prototype_full_path = str(Path(output_path) / prototype_name)

        return {
            "status": status,
            "message": message,
            "results": results,
            "prototype_name": prototype_name,
            "prototype_path": prototype_full_path,
            "success_count": success_count,
            "fail_count": fail_count,
            "next_steps": [
                f"cd {prototype_full_path}",
                "pnpm install",
                "pnpm dev"
            ]
        }

    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "error": traceback.format_exc(),
            "results": []
        }


def main():
    parser = argparse.ArgumentParser(description='批量生成 Vue 原型页面')
    parser.add_argument('--config', '-c', help='JSON配置文件路径')
    parser.add_argument('--input', '-i', help='JSON格式的输入配置')
    parser.add_argument('--output', '-o', help='输出结果到文件')

    args = parser.parse_args()

    # 读取配置
    if args.input:
        config = json.loads(args.input)
    elif args.config:
        config = json.loads(Path(args.config).read_text(encoding='utf-8'))
    else:
        config = json.loads(sys.stdin.read())

    # 执行批量生成
    result = batch_generate(config)

    # 输出结果
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding='utf-8')
    else:
        print(output)

    # 打印下一步操作提示
    if result['status'] in ['success', 'partial']:
        print("\n" + "="*50)
        print("📋 下一步操作:")
        print("="*50)
        for step in result.get('next_steps', []):
            print(f"  {step}")
        print(f"\n🌐 服务启动后，访问 http://localhost:3005 查看原型")

    sys.exit(0 if result['status'] in ['success', 'partial'] else 1)


if __name__ == '__main__':
    main()
