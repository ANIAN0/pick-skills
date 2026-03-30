"""
批量生成原型页面脚本
支持并行生成多个页面原型

用法:
    python batch_generate.py --config <json_config_path>
"""

import argparse
import json
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
from generate_page import generate_page


def batch_generate(pages_config: List[Dict], max_workers: int = 3) -> Dict:
    """批量生成多个页面原型

    Args:
        pages_config: 页面配置列表，每项是一个 generate_page 的配置
        max_workers: 并行线程数

    Returns:
        {
            "results": [{"file_path": "...", "status": "...", ...}],
            "summary": {
                "total": N,
                "success": N,
                "failed": N
            }
        }
    """
    results = []

    def generate_single(page_config: Dict) -> Dict:
        """生成单个页面，用于线程池"""
        try:
            result = generate_page(page_config)
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": f"生成异常: {str(e)}",
                "page_name": page_config.get('page_name', 'unknown')
            }

    # 并行生成页面
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_page = {
            executor.submit(generate_single, config): config
            for config in pages_config
        }

        for future in as_completed(future_to_page):
            page_config = future_to_page[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                results.append({
                    "status": "error",
                    "message": f"线程执行异常: {str(e)}",
                    "page_name": page_config.get('page_name', 'unknown')
                })

    # 汇总结果
    success_count = sum(1 for r in results if r.get('status') == 'success')
    failed_count = len(results) - success_count

    return {
        "results": results,
        "summary": {
            "total": len(results),
            "success": success_count,
            "failed": failed_count
        }
    }


def main():
    parser = argparse.ArgumentParser(description='批量生成原型页面')
    parser.add_argument('--config', '-c', required=True, help='JSON配置文件路径')
    parser.add_argument('--output', '-o', help='输出结果到文件')
    parser.add_argument('--workers', '-w', type=int, default=3, help='并行线程数（默认3）')

    args = parser.parse_args()

    # 读取配置
    config_path = Path(args.config)
    if not config_path.exists():
        print(json.dumps({"error": f"配置文件不存在: {args.config}"}, ensure_ascii=False))
        sys.exit(1)

    config = json.loads(config_path.read_text(encoding='utf-8'))
    pages = config.get('pages', [])

    if not pages:
        print(json.dumps({"error": "配置中没有页面列表"}, ensure_ascii=False))
        sys.exit(1)

    # 批量生成
    result = batch_generate(pages, max_workers=args.workers)

    # 输出结果
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding='utf-8')
    else:
        print(output)

    # 如果有失败的，返回非0退出码
    sys.exit(0 if result['summary']['failed'] == 0 else 1)


if __name__ == '__main__':
    main()
