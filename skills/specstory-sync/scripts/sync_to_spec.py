"""Sync Claude Code conversation history to Specstory-style Markdown files.

Reads the current session's JSONL data from ~/.claude/projects/ and converts
it into formatted Markdown stored in .specstory/history/.

Designed to be called via Claude Code's Stop hook.
"""

import json
import os
import sys
import time
import re
from datetime import datetime, timezone
from pathlib import Path


def find_project_dir(cwd: str) -> Path | None:
    """Map a working directory to its .claude/projects/ subdirectory name.

    Claude Code encodes paths by replacing : and \\ with -, then joining
    segments with -. e.g. D:\\workspace\\foo -> D--workspace-foo
    """
    normalized = cwd.replace("\\", "/").rstrip("/")
    normalized = normalized.replace(":", "-")
    parts = normalized.split("/")
    encoded = "-".join(parts)

    projects_root = Path.home() / ".claude" / "projects"

    candidate = projects_root / encoded
    if candidate.exists():
        return candidate

    for d in projects_root.iterdir():
        if d.is_dir() and d.name.lower() == encoded.lower():
            return d

    return None


def find_active_session(project_dir: Path) -> Path | None:
    """Find the most recently modified session JSONL in the project dir."""
    jsonl_files = list(project_dir.glob("*.jsonl"))
    if not jsonl_files:
        return None
    return max(jsonl_files, key=lambda f: f.stat().st_mtime)


def read_jsonl(path: Path) -> list[dict]:
    """Read a JSONL file, skipping malformed lines."""
    records = []
    for attempt in range(3):
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
            return records
        except (OSError, PermissionError):
            if attempt < 2:
                time.sleep(0.5)
            else:
                raise
    return records


def extract_messages(records: list[dict]) -> list[dict]:
    """Extract user and assistant messages from JSONL records, in order."""
    messages = []
    for rec in records:
        if rec.get("isSidechain"):
            continue
        msg_type = rec.get("type")
        if msg_type not in ("user", "assistant"):
            continue

        ts = rec.get("timestamp", "")
        msg = rec.get("message", {})
        role = msg.get("role", msg_type)
        content = msg.get("content", "")

        messages.append({
            "role": role,
            "content": content,
            "timestamp": ts,
        })
    return messages


def format_content(content) -> str:
    """Format a message content field (string or list) into Markdown."""
    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts = []
        for block in content:
            if not isinstance(block, dict):
                continue
            btype = block.get("type", "")

            if btype == "tool_result":
                raw = block.get("content", "")
                if isinstance(raw, list):
                    text = "\n".join(
                        item.get("text", str(item)) if isinstance(item, dict) else str(item)
                        for item in raw
                    )
                else:
                    text = str(raw)
                if len(text) > 500:
                    text = text[:500] + "\n... (truncated)"
                if text.strip():
                    parts.append(f"<tool-result>\n{text.strip()}\n</tool-result>")

            elif btype == "text":
                text = block.get("text", "")
                if text.strip():
                    parts.append(text.strip())

            elif btype == "tool_use":
                name = block.get("name", "")
                inp = block.get("input", {})
                if name == "Bash" and "command" in inp:
                    cmd = inp["command"]
                    if len(cmd) > 200:
                        cmd = cmd[:200] + "..."
                    parts.append(f"```bash\n{cmd}\n```")
                elif name in ("Read", "Write", "Edit"):
                    fp = inp.get("file_path", inp.get("filePath", ""))
                    parts.append(f"*{name}*: `{fp}`")
                else:
                    inp_str = json.dumps(inp, ensure_ascii=False)
                    if len(inp_str) > 200:
                        inp_str = inp_str[:200] + "..."
                    parts.append(f"*{name}*: {inp_str}")

        return "\n\n".join(parts)

    return str(content).strip()


def render_markdown(messages: list[dict], session_id: str, project_name: str) -> str:
    """Render messages into a Specstory-compatible Markdown document."""
    if not messages:
        return ""

    first_ts = messages[0].get("timestamp", "")
    try:
        dt = datetime.fromisoformat(first_ts.replace("Z", "+00:00"))
        date_str = dt.strftime("%Y-%m-%d %H:%M")
        file_ts = dt.strftime("%Y-%m-%d_%H-%M-%SZ")
    except (ValueError, AttributeError):
        date_str = first_ts
        file_ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%SZ")

    lines = [
        "<!-- Generated by Claude Code Specstory Sync -->",
        "",
        f"# {date_str}",
        "",
        f"<!-- Claude Code Session {session_id} ({first_ts}) -->",
        "",
    ]

    for msg in messages:
        role = msg["role"]
        ts = msg.get("timestamp", "")
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            ts_display = dt.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, AttributeError):
            ts_display = ts

        content = format_content(msg["content"])
        if not content:
            continue

        if role == "user":
            lines.append(f"_**User ({ts_display})**_")
            lines.append("")
            lines.append(content)
        elif role == "assistant":
            lines.append(f"_**Assistant ({ts_display})**_")
            lines.append("")
            lines.append(content)

        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines), file_ts


def compute_message_fingerprint(messages: list[dict]) -> str:
    """Create a lightweight fingerprint of the message sequence for dedup."""
    parts = []
    for m in messages:
        role = m["role"]
        ts = m.get("timestamp", "")
        content = m["content"]
        if isinstance(content, str):
            snippet = content[:100]
        elif isinstance(content, list):
            snippet = str(len(content))
        else:
            snippet = ""
        parts.append(f"{role}|{ts}|{snippet}")
    return str(hash("|".join(parts)))


def sync(cwd: str):
    """Main sync function."""
    project_dir = find_project_dir(cwd)
    if project_dir is None:
        print(f"[specstory-sync] No .claude/projects/ directory found for: {cwd}", file=sys.stderr)
        return

    session_path = find_active_session(project_dir)
    if session_path is None:
        print(f"[specstory-sync] No session JSONL found in {project_dir}", file=sys.stderr)
        return

    session_id = session_path.stem

    records = read_jsonl(session_path)
    messages = extract_messages(records)
    if not messages:
        return

    specstory_dir = Path(cwd) / ".specstory" / "history"
    specstory_dir.mkdir(parents=True, exist_ok=True)

    fingerprint_file = specstory_dir / f".{session_id}.fp"
    new_fp = compute_message_fingerprint(messages)
    if fingerprint_file.exists():
        old_fp = fingerprint_file.read_text(encoding="utf-8").strip()
        if old_fp == new_fp:
            return

    project_name = Path(cwd).name
    result = render_markdown(messages, session_id, project_name)
    if result is None:
        return
    md_content, file_ts = result

    existing = list(specstory_dir.glob(f"*{session_id[:8]}*"))
    if existing:
        output_path = existing[0]
    else:
        _skip_prefixes = ("<local-command-", "<command-", "Base directory for this skill")
        title = ""
        for m in messages:
            if m["role"] != "user":
                continue
            text = ""
            if isinstance(m["content"], str):
                text = m["content"].strip()
            elif isinstance(m["content"], list):
                for block in m["content"]:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text = block.get("text", "").strip()
                        break
            if not text or any(text.startswith(p) for p in _skip_prefixes):
                continue
            title = text[:60]
            title = re.sub(r'[\s/\\:*?"<>|]+', '-', title)
            title = re.sub(r'[^\w\-.]', '', title.encode('ascii', 'ignore').decode('ascii'))
            title = title.strip('-')[:40]
            break
        suffix = f"-{title}" if title else ""
        output_path = specstory_dir / f"{file_ts}{suffix}.md"

    output_path.write_text(md_content, encoding="utf-8")
    fingerprint_file.write_text(new_fp, encoding="utf-8")

    print(f"[specstory-sync] Synced {len(messages)} messages -> {output_path.name}")


if __name__ == "__main__":
    cwd = os.environ.get("CLAUDE_PROJECT_CWD", os.environ.get("CLAUDE_CWD", os.getcwd()))
    sync(cwd)
