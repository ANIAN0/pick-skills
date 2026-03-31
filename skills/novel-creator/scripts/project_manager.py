#!/usr/bin/env python3
"""
小说项目管理系统
负责项目初始化、配置管理和文件结构维护
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# 默认项目配置
DEFAULT_CONFIG = {
    "project_name": "",
    "version": "1.0.0",
    "created_at": "",
    "settings": {
        "target_word_count": 100000,
        "estimated_chapters": 100,
        "genre": "",
        "sub_genre": "",
        "style": "",
        "language": "zh-CN",
        "target_audience": ""
    },
    "kb_sync": {
        "chunk_size": 500,
        "chunk_overlap": 100,
        "db_path": ".novel/vector-index/novel_kb.db"
    },
    "phases": {
        "topic": {"name": "选题", "order": 1},
        "logline": {"name": "一句话故事", "order": 2},
        "world": {"name": "世界观", "order": 3},
        "characters": {"name": "角色", "order": 4},
        "outline": {"name": "大纲", "order": 5},
        "volumes": {"name": "分卷", "order": 6},
        "storylines": {"name": "故事线", "order": 7},
        "chapter_plans": {"name": "章纲", "order": 8},
        "draft": {"name": "草稿", "order": 9},
        "polish": {"name": "润色", "order": 10},
        "review": {"name": "审查", "order": 11}
    }
}

# 项目目录结构
PROJECT_DIRS = [
    ".novel",
    ".novel/vector-index",
    "00-选题",
    "01-世界观",
    "02-角色",
    "03-大纲",
    "04-分卷",
    "05-故事线",
    "06-章纲",
    "07-正文",
    "08-素材"
]


def find_project_root(start_path: Optional[str] = None) -> Optional[str]:
    """
    查找项目根目录（向上查找包含 .novel 目录的目录）

    Args:
        start_path: 起始搜索路径，默认为当前目录

    Returns:
        项目根目录路径，未找到返回 None
    """
    if start_path is None:
        start_path = Path.cwd()
    else:
        start_path = Path(start_path)

    for parent in [start_path] + list(start_path.parents):
        if (parent / ".novel").exists():
            return str(parent)

    return None


def is_project_initialized(path: str) -> bool:
    """检查指定路径是否已初始化小说项目"""
    novel_dir = Path(path) / ".novel"
    config_file = novel_dir / "config.json"
    return novel_dir.exists() and config_file.exists()


def init_project(project_name: str, path: Optional[str] = None, **settings) -> str:
    """
    初始化新小说项目

    Args:
        project_name: 项目名称
        path: 项目路径，默认为当前目录/项目名
        **settings: 额外的项目设置

    Returns:
        项目根目录路径
    """
    if path is None:
        # 使用项目名作为目录名（清理非法字符）
        safe_name = "".join(c if c.isalnum() or c in "_-" else "_" for c in project_name)
        path = Path.cwd() / safe_name
    else:
        path = Path(path)

    # 创建目录结构
    for dir_name in PROJECT_DIRS:
        (path / dir_name).mkdir(parents=True, exist_ok=True)

    # 创建配置文件
    config = DEFAULT_CONFIG.copy()
    config["project_name"] = project_name
    config["created_at"] = datetime.now().isoformat()
    config["settings"].update(settings)

    config_path = path / ".novel" / "config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    # 创建初始状态文件
    state = {
        "project_name": project_name,
        "current_phase": "",
        "phases": {},
        "last_updated": datetime.now().isoformat()
    }

    state_path = path / ".novel" / "state.json"
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

    # 创建 README
    readme_content = f"""# {project_name}

小说创作项目

## 项目结构

```
{project_name}/
├── .novel/           # 项目配置
├── 00-选题/          # 选题与定位
├── 01-世界观/        # 世界观设定
├── 02-角色/          # 角色设定
├── 03-大纲/          # 整体大纲
├── 04-分卷/          # 分卷结构
├── 05-故事线/        # 故事线设计
├── 06-章纲/          # 章纲
├── 07-正文/          # 章节正文
└── 08-素材/          # 参考资料
```

## 开始创作

使用 novel-creator 技能开始创作流程。

## 创建时间

{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

    with open(path / "README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)

    return str(path)


def load_config(project_path: Optional[str] = None) -> Dict:
    """
    加载项目配置

    Args:
        project_path: 项目路径，默认自动查找

    Returns:
        配置字典

    Raises:
        FileNotFoundError: 未找到配置文件
    """
    if project_path is None:
        project_path = find_project_root()
        if project_path is None:
            raise FileNotFoundError("未找到小说项目（缺少 .novel 目录）")

    config_path = Path(project_path) / ".novel" / "config.json"

    if not config_path.exists():
        raise FileNotFoundError(f"项目配置文件不存在: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(config: Dict, project_path: Optional[str] = None) -> None:
    """
    保存项目配置

    Args:
        config: 配置字典
        project_path: 项目路径，默认自动查找
    """
    if project_path is None:
        project_path = find_project_root()
        if project_path is None:
            raise FileNotFoundError("未找到小说项目（缺少 .novel 目录）")

    config_path = Path(project_path) / ".novel" / "config.json"

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def update_config(updates: Dict, project_path: Optional[str] = None) -> Dict:
    """
    更新项目配置

    Args:
        updates: 要更新的配置项
        project_path: 项目路径

    Returns:
        更新后的配置
    """
    config = load_config(project_path)

    def deep_update(d: Dict, u: Dict) -> Dict:
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                d[k] = deep_update(d[k], v)
            else:
                d[k] = v
        return d

    config = deep_update(config, updates)
    save_config(config, project_path)

    return config


def get_project_info(project_path: Optional[str] = None) -> Dict:
    """
    获取项目完整信息

    Returns:
        包含配置、状态、统计信息的字典
    """
    config = load_config(project_path)

    if project_path is None:
        project_path = find_project_root()

    # 加载状态
    state_path = Path(project_path) / ".novel" / "state.json"
    if state_path.exists():
        with open(state_path, "r", encoding="utf-8") as f:
            state = json.load(f)
    else:
        state = {}

    # 统计文件
    stats = {}
    content_dirs = ["00-选题", "01-世界观", "02-角色", "03-大纲",
                   "04-分卷", "05-故事线", "06-章纲", "07-正文"]

    for dir_name in content_dirs:
        dir_path = Path(project_path) / dir_name
        if dir_path.exists():
            md_files = list(dir_path.rglob("*.md"))
            stats[dir_name] = len(md_files)
        else:
            stats[dir_name] = 0

    return {
        "config": config,
        "state": state,
        "stats": stats,
        "path": project_path
    }


def list_projects(search_path: str = ".") -> List[Dict]:
    """
    列出指定路径下的所有小说项目

    Args:
        search_path: 搜索路径

    Returns:
        项目信息列表
    """
    projects = []
    search_path = Path(search_path).resolve()

    # 搜索子目录中的.novel文件夹
    for novel_dir in search_path.rglob(".novel"):
        if novel_dir.is_dir():
            project_path = novel_dir.parent
            config_path = novel_dir / "config.json"

            if config_path.exists():
                try:
                    with open(config_path, "r", encoding="utf-8") as f:
                        config = json.load(f)

                    projects.append({
                        "name": config.get("project_name", "Unknown"),
                        "path": str(project_path),
                        "created": config.get("created_at", ""),
                        "genre": config.get("settings", {}).get("genre", "")
                    })
                except Exception:
                    pass

    return projects


def ensure_dir(dir_path: str) -> Path:
    """确保目录存在，不存在则创建"""
    path = Path(dir_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_output_path(phase: str, filename: str, project_path: Optional[str] = None) -> Path:
    """
    获取阶段产出文件的标准路径

    Args:
        phase: 阶段名称（如：topic, world, characters）
        filename: 文件名
        project_path: 项目路径

    Returns:
        完整的文件路径
    """
    phase_to_dir = {
        "topic": "00-选题",
        "logline": "00-选题",
        "world": "01-世界观",
        "characters": "02-角色",
        "outline": "03-大纲",
        "volumes": "04-分卷",
        "storylines": "05-故事线",
        "chapter_plans": "06-章纲",
        "draft": "07-正文",
        "polish": "07-正文",
        "review": "07-正文"
    }

    if project_path is None:
        project_path = find_project_root()
        if project_path is None:
            raise FileNotFoundError("未找到小说项目")

    dir_name = phase_to_dir.get(phase, phase)
    dir_path = Path(project_path) / dir_name
    ensure_dir(dir_path)

    return dir_path / filename


# ============ CLI 接口 ============

def main():
    import argparse

    parser = argparse.ArgumentParser(description="小说项目管理工具")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # init 命令
    init_parser = subparsers.add_parser("init", help="初始化新项目")
    init_parser.add_argument("name", help="项目名称")
    init_parser.add_argument("--path", "-p", help="项目路径")
    init_parser.add_argument("--genre", "-g", help="小说类型")
    init_parser.add_argument("--word-count", "-w", type=int, default=100000,
                           help="目标字数")

    # info 命令
    info_parser = subparsers.add_parser("info", help="显示项目信息")
    info_parser.add_argument("--path", "-p", help="项目路径")

    # list 命令
    list_parser = subparsers.add_parser("list", help="列出项目")
    list_parser.add_argument("--path", "-p", default=".", help="搜索路径")

    # config 命令
    config_parser = subparsers.add_parser("config", help="查看/修改配置")
    config_parser.add_argument("--get", help="获取配置项（如：settings.genre）")
    config_parser.add_argument("--set", help="设置配置项（JSON格式）")

    args = parser.parse_args()

    if args.command == "init":
        settings = {
            "target_word_count": args.word_count
        }
        if args.genre:
            settings["genre"] = args.genre

        project_path = init_project(args.name, args.path, **settings)
        print(f"项目已创建: {project_path}")
        print(f"项目名: {args.name}")

    elif args.command == "info":
        try:
            info = get_project_info(args.path)
            print("=" * 50)
            print(f"项目: {info['config']['project_name']}")
            print(f"路径: {info['path']}")
            print(f"类型: {info['config']['settings'].get('genre', '未设置')}")
            print(f"目标字数: {info['config']['settings'].get('target_word_count', '未设置')}")
            print("=" * 50)
            print("\n文件统计:")
            for dir_name, count in info['stats'].items():
                if count > 0:
                    print(f"  {dir_name}: {count} 个文件")
        except FileNotFoundError as e:
            print(f"错误: {e}")
            return 1

    elif args.command == "list":
        projects = list_projects(args.path)
        if projects:
            print(f"找到 {len(projects)} 个项目:")
            for p in projects:
                print(f"  - {p['name']} ({p['genre'] or '未分类'}) @ {p['path']}")
        else:
            print("未找到项目")

    elif args.command == "config":
        if args.get:
            config = load_config()
            keys = args.get.split(".")
            value = config
            for key in keys:
                value = value.get(key, "未找到")
            print(f"{args.get} = {value}")
        elif args.set:
            try:
                updates = json.loads(args.set)
                config = update_config(updates)
                print("配置已更新")
            except json.JSONDecodeError:
                print("错误: 无效的 JSON 格式")
                return 1
        else:
            config = load_config()
            print(json.dumps(config, indent=2, ensure_ascii=False))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
