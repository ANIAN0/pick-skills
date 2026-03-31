#!/usr/bin/env python3
"""
小说项目状态管理系统
负责创作进度追踪、阶段管理和状态持久化
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# 创作阶段定义
PHASES = {
    "topic": {"name": "选题", "order": 1, "description": "确定小说主题和方向"},
    "logline": {"name": "一句话故事", "order": 2, "description": "用一句话概括故事核心"},
    "world": {"name": "世界观", "order": 3, "description": "构建世界规则和背景"},
    "characters": {"name": "角色", "order": 4, "description": "设计人物角色"},
    "outline": {"name": "大纲", "order": 5, "description": "创建整体故事结构"},
    "volumes": {"name": "分卷", "order": 6, "description": "规划分卷结构"},
    "storylines": {"name": "故事线", "order": 7, "description": "设计主线、暗线、感情线"},
    "chapter_plans": {"name": "章纲", "order": 8, "description": "创建章节大纲"},
    "draft": {"name": "草稿", "order": 9, "description": "撰写章节初稿"},
    "polish": {"name": "润色", "order": 10, "description": "优化文字质量"},
    "review": {"name": "审查", "order": 11, "description": "检查一致性和问题"}
}

# 阶段依赖关系
DEPENDENCIES = {
    "outline": ["topic", "world", "characters"],
    "volumes": ["outline"],
    "storylines": ["outline"],
    "chapter_plans": ["volumes", "storylines"],
    "draft": ["chapter_plans"],
    "polish": ["draft"],
    "review": ["draft"]
}


@dataclass
class PhaseInfo:
    """阶段信息"""
    status: str  # pending, in_progress, completed, skipped
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    output_files: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.output_files is None:
            self.output_files = []
        if self.metadata is None:
            self.metadata = {}


class StateManager:
    """项目状态管理器"""

    def __init__(self, project_path: Optional[str] = None):
        self.project_path = project_path or self._find_project_root()
        if not self.project_path:
            raise FileNotFoundError("未找到小说项目（缺少 .novel 目录）")

        self.state_file = Path(self.project_path) / ".novel" / "state.json"
        self.state = self._load_state()

    def _find_project_root(self) -> Optional[str]:
        """查找项目根目录"""
        current = Path.cwd()
        for parent in [current] + list(current.parents):
            if (parent / ".novel").exists():
                return str(parent)
        return None

    def _load_state(self) -> Dict:
        """加载状态文件"""
        if self.state_file.exists():
            with open(self.state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return self._create_initial_state()

    def _create_initial_state(self) -> Dict:
        """创建初始状态"""
        return {
            "project_name": "",
            "current_phase": "",
            "phases": {},
            "last_updated": datetime.now().isoformat()
        }

    def _save_state(self) -> None:
        """保存状态文件"""
        self.state["last_updated"] = datetime.now().isoformat()
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def get_phase_info(self, phase: str) -> PhaseInfo:
        """获取阶段信息"""
        phase_data = self.state.get("phases", {}).get(phase, {})
        return PhaseInfo(
            status=phase_data.get("status", "pending"),
            started_at=phase_data.get("started_at"),
            completed_at=phase_data.get("completed_at"),
            output_files=phase_data.get("output_files", []),
            metadata=phase_data.get("metadata", {})
        )

    def update_phase(self, phase: str, **kwargs) -> None:
        """更新阶段信息"""
        if "phases" not in self.state:
            self.state["phases"] = {}

        if phase not in self.state["phases"]:
            self.state["phases"][phase] = {}

        for key, value in kwargs.items():
            self.state["phases"][phase][key] = value

        self._save_state()

    def start_phase(self, phase: str) -> None:
        """开始一个阶段"""
        self.update_phase(
            phase,
            status="in_progress",
            started_at=datetime.now().isoformat()
        )
        self.state["current_phase"] = phase
        self._save_state()

    def complete_phase(self, phase: str, output_files: List[str] = None) -> None:
        """完成一个阶段"""
        updates = {
            "status": "completed",
            "completed_at": datetime.now().isoformat()
        }

        if output_files:
            current_files = self.state.get("phases", {}).get(phase, {}).get("output_files", [])
            updates["output_files"] = current_files + output_files

        self.update_phase(phase, **updates)

    def skip_phase(self, phase: str) -> None:
        """跳过一个阶段"""
        self.update_phase(
            phase,
            status="skipped",
            completed_at=datetime.now().isoformat()
        )

    def get_current_phase(self) -> str:
        """获取当前阶段"""
        return self.state.get("current_phase", "")

    def get_phase_status(self, phase: str) -> str:
        """获取阶段状态"""
        return self.state.get("phases", {}).get(phase, {}).get("status", "pending")

    def is_phase_completed(self, phase: str) -> bool:
        """检查阶段是否已完成"""
        return self.get_phase_status(phase) == "completed"

    def is_phase_in_progress(self, phase: str) -> bool:
        """检查阶段是否进行中"""
        return self.get_phase_status(phase) == "in_progress"

    def get_dependencies(self, phase: str) -> List[str]:
        """获取阶段的依赖"""
        return DEPENDENCIES.get(phase, [])

    def check_dependencies(self, phase: str) -> Dict[str, bool]:
        """检查阶段依赖是否满足"""
        deps = self.get_dependencies(phase)
        return {dep: self.is_phase_completed(dep) for dep in deps}

    def are_dependencies_met(self, phase: str) -> bool:
        """检查所有依赖是否都已满足"""
        deps_status = self.check_dependencies(phase)
        return all(deps_status.values()) if deps_status else True

    def get_missing_dependencies(self, phase: str) -> List[str]:
        """获取未完成的依赖"""
        deps_status = self.check_dependencies(phase)
        return [dep for dep, completed in deps_status.items() if not completed]

    def get_progress(self) -> Dict[str, Any]:
        """获取整体进度"""
        total_phases = len(PHASES)
        completed = sum(
            1 for phase in PHASES
            if self.is_phase_completed(phase)
        )
        in_progress = sum(
            1 for phase in PHASES
            if self.is_phase_in_progress(phase)
        )

        return {
            "total": total_phases,
            "completed": completed,
            "in_progress": in_progress,
            "pending": total_phases - completed - in_progress,
            "percentage": (completed / total_phases * 100) if total_phases > 0 else 0
        }

    def get_next_phase(self) -> Optional[str]:
        """获取下一个待进行的阶段"""
        for phase_id, phase_info in sorted(PHASES.items(), key=lambda x: x[1]["order"]):
            status = self.get_phase_status(phase_id)
            if status in ["pending", "skipped"]:
                return phase_id
        return None

    def add_output_file(self, phase: str, file_path: str) -> None:
        """添加产出文件"""
        current_files = self.state.get("phases", {}).get(phase, {}).get("output_files", [])
        if file_path not in current_files:
            current_files.append(file_path)
            self.update_phase(phase, output_files=current_files)

    def get_output_files(self, phase: str) -> List[str]:
        """获取阶段的产出文件"""
        return self.state.get("phases", {}).get(phase, {}).get("output_files", [])

    def set_metadata(self, phase: str, key: str, value: Any) -> None:
        """设置阶段元数据"""
        metadata = self.state.get("phases", {}).get(phase, {}).get("metadata", {})
        metadata[key] = value
        self.update_phase(phase, metadata=metadata)

    def get_metadata(self, phase: str, key: str, default: Any = None) -> Any:
        """获取阶段元数据"""
        return self.state.get("phases", {}).get(phase, {}).get("metadata", {}).get(key, default)

    def get_summary(self) -> Dict[str, Any]:
        """获取状态摘要"""
        progress = self.get_progress()
        current = self.get_current_phase()

        return {
            "project_name": self.state.get("project_name", ""),
            "current_phase": current,
            "current_phase_name": PHASES.get(current, {}).get("name", "未开始"),
            "progress": progress,
            "phases": {
                phase_id: {
                    "name": info["name"],
                    "status": self.get_phase_status(phase_id)
                }
                for phase_id, info in PHASES.items()
            }
        }


def format_status_summary(manager: StateManager) -> str:
    """格式化状态摘要为可读文本"""
    summary = manager.get_summary()
    progress = summary["progress"]

    lines = [
        "=" * 50,
        f"项目: {summary['project_name']}",
        "=" * 50,
        "",
        f"当前阶段: {summary['current_phase_name']}",
        f"总进度: {progress['completed']}/{progress['total']} ({progress['percentage']:.1f}%)",
        "",
        "阶段状态:"
    ]

    for phase_id, phase_info in summary["phases"].items():
        status = phase_info["status"]
        status_icon = {
            "completed": "✓",
            "in_progress": "▶",
            "skipped": "⊘",
            "pending": "○"
        }.get(status, "○")

        lines.append(f"  {status_icon} {phase_info['name']}")

    lines.append("")
    return "\n".join(lines)


# ============ CLI 接口 ============

def main():
    import argparse

    parser = argparse.ArgumentParser(description="小说项目状态管理")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # status 命令
    status_parser = subparsers.add_parser("status", help="显示项目状态")

    # start 命令
    start_parser = subparsers.add_parser("start", help="开始一个阶段")
    start_parser.add_argument("phase", choices=list(PHASES.keys()), help="阶段名称")

    # complete 命令
    complete_parser = subparsers.add_parser("complete", help="完成一个阶段")
    complete_parser.add_argument("phase", choices=list(PHASES.keys()), help="阶段名称")
    complete_parser.add_argument("--files", "-f", nargs="+", help="产出文件")

    # skip 命令
    skip_parser = subparsers.add_parser("skip", help="跳过一个阶段")
    skip_parser.add_argument("phase", choices=list(PHASES.keys()), help="阶段名称")

    # check 命令
    check_parser = subparsers.add_parser("check", help="检查阶段依赖")
    check_parser.add_argument("phase", choices=list(PHASES.keys()), help="阶段名称")

    # next 命令
    next_parser = subparsers.add_parser("next", help="显示下一个阶段")

    args = parser.parse_args()

    try:
        manager = StateManager()
    except FileNotFoundError as e:
        print(f"错误: {e}")
        return 1

    if args.command == "status":
        print(format_status_summary(manager))

    elif args.command == "start":
        # 检查依赖
        missing = manager.get_missing_dependencies(args.phase)
        if missing:
            missing_names = [PHASES[m]["name"] for m in missing]
            print(f"警告: 以下依赖阶段尚未完成: {', '.join(missing_names)}")
            print("是否继续? (y/n)")
            response = input().strip().lower()
            if response != "y":
                return 0

        manager.start_phase(args.phase)
        phase_name = PHASES[args.phase]["name"]
        print(f"已开始阶段: {phase_name}")

    elif args.command == "complete":
        manager.complete_phase(args.phase, args.files or [])
        phase_name = PHASES[args.phase]["name"]
        print(f"已完成阶段: {phase_name}")

    elif args.command == "skip":
        manager.skip_phase(args.phase)
        phase_name = PHASES[args.phase]["name"]
        print(f"已跳过阶段: {phase_name}")

    elif args.command == "check":
        deps = manager.check_dependencies(args.phase)
        phase_name = PHASES[args.phase]["name"]
        print(f"阶段: {phase_name}")
        print("依赖状态:")
        for dep, completed in deps.items():
            dep_name = PHASES[dep]["name"]
            status = "✓ 已完成" if completed else "✗ 未完成"
            print(f"  {dep_name}: {status}")

    elif args.command == "next":
        next_phase = manager.get_next_phase()
        if next_phase:
            phase_name = PHASES[next_phase]["name"]
            print(f"下一个阶段: {phase_name}")
        else:
            print("所有阶段已完成")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
