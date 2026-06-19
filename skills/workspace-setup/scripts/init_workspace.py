#!/usr/bin/env python3
"""
初始化工作区脚本
下载通用 CLAUDE.md、AGENTS.md，创建项目规则和项目知识库入口。
"""

import os
import json
import argparse
import sys
from pathlib import Path
from typing import Dict, List

from filebrowser_client import load_config, get_client, get_remote_path

PERSONAL_KB_SCRIPTS = Path(__file__).resolve().parents[2] / "personal-kb" / "scripts"
if str(PERSONAL_KB_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(PERSONAL_KB_SCRIPTS))
from kb_cli import check_global, init_project  # noqa: E402


# 版本目录结构
VERSION_SUBDIRS = [
    "requirements",   # 需求文档
    "references",     # 参考文档
    "prototypes",     # 原型设计
    "tech-design",    # 技术方案
    "plan",           # 实施计划
    "tests"           # 测试文件
]

# 版本之外可长期复用的工作区目录。
WORKPLACE_GLOBAL_DIRS = [
    "global",          # 可复用的方案、模板、脚本和资产
    "test"             # 可复用的测试方案、测试脚本、夹具和报告模板
]

# 通用配置文件列表：这些文件应在所有项目中保持一致。
CONFIG_FILES = ["CLAUDE.md", "AGENTS.md"]

# 项目级默认文件和目录：每个项目独立维护，不参与通用配置包同步。
DEFAULT_PROJECT_RULES_FILE = "PROJECT_RULES.md"
DEFAULT_PROJECT_KB_DIR = "project-kb"
DEFAULT_GLOBAL_KB_DIR = "~/personal-kb"


def resolve_knowledge_global_dir(config: Dict, project_root: Path) -> tuple[Path, bool, str | None]:
    """委托 personal-kb 检查全局研究知识库边界。"""
    knowledge_config = config.get("knowledge", {})
    configured = knowledge_config.get("global_dir")
    raw_path = configured or DEFAULT_GLOBAL_KB_DIR
    expanded = Path(os.path.expandvars(os.path.expanduser(raw_path)))
    if not expanded.is_absolute():
        raw_path = str((project_root / expanded).resolve())
    result = check_global(raw_path, explicit=configured is not None)
    return Path(result["root"]), bool(result["available"]), result["error"]


def init_workspace(config_path: str, download_configs: bool = True) -> Dict:
    """初始化工作区"""
    print("\n[START] 开始初始化工作区...\n")

    # 加载配置
    config = load_config(config_path)
    ws_config = config.get("workspace", {})
    project_root = Path(config_path).parent

    # 获取配置
    workplace_dir = ws_config.get("workplace_dir", "workplace")
    current_version = ws_config.get("current_version", "1.0")
    project_rules_file = ws_config.get("project_rules_file", DEFAULT_PROJECT_RULES_FILE)
    project_kb_dir = ws_config.get("project_kb_dir", DEFAULT_PROJECT_KB_DIR)
    knowledge_global_dir, knowledge_available, knowledge_error = resolve_knowledge_global_dir(
        config,
        project_root,
    )

    results = {
        "directories_created": [],
        "configs_downloaded": [],
        "configs_created": [],
        "knowledge_files_created": [],
        "warnings": [],
        "errors": [],
        "knowledge_global_dir": str(knowledge_global_dir),
        "knowledge_available": knowledge_available,
        "knowledge_error": knowledge_error,
    }

    # 1. 创建workplace目录
    workplace_path = project_root / workplace_dir
    workplace_path.mkdir(exist_ok=True)
    results["directories_created"].append(str(workplace_path))
    print(f"[OK] 创建工作目录: {workplace_path}")

    # 2. 创建长期复用目录和archive目录
    for subdir in WORKPLACE_GLOBAL_DIRS:
        global_path = workplace_path / subdir
        global_path.mkdir(exist_ok=True)
        results["directories_created"].append(str(global_path))
        print(f"[OK] 创建全局目录: {global_path}")

    archive_path = workplace_path / "archive"
    archive_path.mkdir(exist_ok=True)
    results["directories_created"].append(str(archive_path))
    print(f"[OK] 创建归档目录: {archive_path}")

    # 3. 创建当前版本目录
    version_path = workplace_path / current_version
    version_path.mkdir(exist_ok=True)
    results["directories_created"].append(str(version_path))
    print(f"[OK] 创建版本目录: {version_path}")

    # 4. 创建版本子目录
    for subdir in VERSION_SUBDIRS:
        subdir_path = version_path / subdir
        subdir_path.mkdir(exist_ok=True)
        results["directories_created"].append(str(subdir_path))
        print(f"  - {subdir}/")

    # 5. 创建当前版本的项目图目录。源节点和派生输出分离。
    graph_path = version_path / "graph"
    for graph_subdir in ("nodes", ".derived"):
        subdir_path = graph_path / graph_subdir
        subdir_path.mkdir(parents=True, exist_ok=True)
        results["directories_created"].append(str(subdir_path))
        print(f"  - graph/{graph_subdir}/")

    if knowledge_error:
        results["errors"].append(knowledge_error)
        print(f"[FAIL] {knowledge_error}")
    else:
        print(f"[OK] 全局知识库路径: {knowledge_global_dir}")

    # 6. 处理通用配置文件
    if download_configs and config.get("filebrowser"):
        print(f"\n[DOWNLOAD] 从 filebrowser 下载配置文件...")
        client = get_client(config)
        if client.login():
            for filename in CONFIG_FILES:
                local_path = project_root / filename
                remote_path = get_remote_path(config, filename)

                if client.download_file(remote_path, str(local_path)):
                    results["configs_downloaded"].append(filename)
                else:
                    # 文件不存在，创建空模板
                    create_config_template(
                        local_path,
                        filename,
                        project_rules_file,
                        project_kb_dir
                    )
                    results["configs_created"].append(filename)
        else:
            results["errors"].append("filebrowser登录失败")
            # 创建默认配置文件
            for filename in CONFIG_FILES:
                local_path = project_root / filename
                create_config_template(
                    local_path,
                    filename,
                    project_rules_file,
                    project_kb_dir
                )
                results["configs_created"].append(filename)
    else:
        # 不下载时创建默认配置文件
        print(f"\n[WRITE] 创建默认配置文件...")
        for filename in CONFIG_FILES:
            local_path = project_root / filename
            if not local_path.exists():
                create_config_template(
                    local_path,
                    filename,
                    project_rules_file,
                    project_kb_dir
                )
                results["configs_created"].append(filename)

    # 7. 创建项目独立规则和知识库入口
    create_project_rules_template(project_root / project_rules_file, project_kb_dir)
    kb_result = init_project(
        project_root,
        project_kb_dir=project_kb_dir,
        project_rules_file=project_rules_file,
    )
    results["personal_kb"] = kb_result
    results["knowledge_files_created"].extend(kb_result["created"])
    results["warnings"].extend(kb_result.get("warnings", []))
    if kb_result.get("error"):
        results["errors"].append(kb_result["error"])

    # 8. 更新配置中的当前版本
    update_config_version(config_path, current_version)

    # 输出结果
    print(f"\n[STATS] 初始化完成:")
    print(f"   目录创建: {len(results['directories_created'])}")
    print(f"   配置下载: {len(results['configs_downloaded'])}")
    print(f"   配置创建: {len(results['configs_created'])}")

    if results["errors"]:
        print(f"   错误: {len(results['errors'])}")
        for err in results["errors"]:
            print(f"   [FAIL] {err}")

    return results


def create_config_template(
    filepath: Path,
    filename: str,
    project_rules_file: str = DEFAULT_PROJECT_RULES_FILE,
    project_kb_dir: str = DEFAULT_PROJECT_KB_DIR
):
    """创建配置文件模板"""
    if filepath.exists():
        return
    templates = {
        "CLAUDE.md": "@AGENTS.md\n",
        "AGENTS.md": (
            "# AGENTS.md\n\n"
            "本文件是所有项目通用的 AI 编码入口。项目相关规则必须维护在同级 "
            f"`{project_rules_file}` 中，避免把通用规则和项目规则混在一起。\n\n"
            "## 必读顺序\n\n"
            "1. 先阅读本文件，遵守通用协作、编码和验证规则。\n"
            f"2. 再阅读同级 `{project_rules_file}`，了解当前项目的规则、重要文件和知识库入口。\n"
            f"3. 修改代码前，阅读 `{project_kb_dir}/code/` 中与目标代码文件对应的说明文档。\n\n"
            "## 编码前先思考\n\n"
            "**不要假设。不要隐藏困惑。揭示权衡。**\n\n"
            "- 明确陈述关键假设。\n"
            "- 如果存在多种解释，先指出差异。\n"
            "- 如果有更简单的方案，说明取舍。\n"
            "- 如果信息不足且影响实现安全，先澄清。\n\n"
            "## 简洁优先\n\n"
            "**用最少的改动解决问题，不做推测性设计。**\n\n"
            "- 不添加未被请求的功能。\n"
            "- 不为一次性代码创建抽象。\n"
            "- 不添加未被请求的灵活性或配置项。\n"
            "- 不为不现实的场景编写复杂错误处理。\n"
            "- 如果实现明显过度复杂，应简化。\n\n"
            "## 精准修改\n\n"
            "**只改必须改的，只清理自己造成的问题。**\n\n"
            "- 不顺手重构无关代码。\n"
            "- 不改动无关注释、格式或命名。\n"
            "- 匹配项目现有风格。\n"
            "- 删除因本次修改变得未使用的导入、变量或函数。\n"
            "- 发现无关问题可以记录或告知，但不要擅自扩大修改范围。\n\n"
            "## 目标驱动执行\n\n"
            "**定义成功标准，并验证到通过。**\n\n"
            "- 修复 bug 时，优先用测试或可复现步骤证明问题已解决。\n"
            "- 重构时，确认重构前后的行为一致。\n"
            "- 多步骤任务应先给出简短计划，再逐步验证。\n\n"
            "## 语言和注释\n\n"
            "- 与用户沟通默认使用中文。\n"
            "- 代码注释遵守项目规则。\n"
            "- 注释解释“为什么”，避免复述“是什么”。\n\n"
            "## Git 操作\n\n"
            "- 可以执行本地 `git status`、`git diff`、`git add`、`git commit` 等操作。\n"
            "- 禁止未经用户明确要求推送远程分支。\n"
            "- 不回滚用户已有改动，除非用户明确要求。\n\n"
            "## 文档同步\n\n"
            "- 通用规则修改后，应同步到所有项目共用的 `AGENTS.md` 模板。\n"
            f"- 项目规则修改到同级 `{project_rules_file}`。\n"
            f"- 代码文件功能、关联、重要逻辑或测试映射变化后，同步更新 `{project_kb_dir}/code/` 中对应说明文档。\n"
        )
    }

    content = templates.get(filename, f"# {filename}\n\n")
    filepath.write_text(content, encoding='utf-8')
    print(f"[OK] 创建模板: {filename}")


def create_project_rules_template(filepath: Path, project_kb_dir: str):
    """创建项目规则模板。已存在时不覆盖，避免破坏项目独立维护的内容。"""
    if filepath.exists():
        return

    content = f"""# 项目规则

本文件是第 2 层项目规则文档，记录所有在当前项目修改代码前必须知道的信息。

## 项目概览

- 项目名称：待补充
- 项目类型：待补充
- 核心目标：待补充

## 必须遵守的项目规则

- 待补充项目特有的编码、测试、发布、目录和安全规则。
- 如果规则适用于所有项目，应上移到 `AGENTS.md`，不要留在本文件。

## 重要文件和目录

| 路径 | 作用 | 修改前必须阅读 |
|---|---|---|
| `README.md` | 项目入口说明 | 是 |
| `{project_kb_dir}/` | 第 3 层项目知识库 | 是 |

## 项目知识库入口

- 知识库根目录：[[{project_kb_dir}/README]]
- 代码文件说明：[[{project_kb_dir}/code/README]]
- 修改任意代码文件前，先阅读与源码路径对应的说明文档。
- 新增、删除或重命名代码文件时，同步新增、删除或移动对应说明文档。

## 验证命令

| 场景 | 命令 | 说明 |
|---|---|---|
| 全量检查 | 待补充 | 当前项目的全量验证方式 |
| 定向测试 | 待补充 | 根据知识库条目选择相关测试 |

## 更新要求

- 修改项目规则时，同时确认 `AGENTS.md` 的通用入口仍然适用。
- 修改代码时，同步更新 `{project_kb_dir}/code/` 下对应说明文档。
- 发现重要项目知识缺失时，补充到本文件或第 3 层知识库。
"""
    filepath.write_text(content, encoding="utf-8")
    print(f"[OK] 创建项目规则模板: {filepath.name}")


def update_config_version(config_path: str, version: str):
    """更新配置文件中的版本号"""
    config = load_config(config_path)
    if config.get("workspace", {}).get("current_version") == version:
        return
    config.setdefault("workspace", {})
    config["workspace"]["current_version"] = version

    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description="初始化工作区")

    parser.add_argument(
        "--config",
        default="skillconfig.json",
        help="配置文件路径"
    )

    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="跳过从filebrowser下载配置文件"
    )

    args = parser.parse_args()

    results = init_workspace(
        config_path=args.config,
        download_configs=not args.skip_download
    )
    return 1 if results["knowledge_error"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
