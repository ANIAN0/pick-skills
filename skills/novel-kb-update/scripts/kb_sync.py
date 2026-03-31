#!/usr/bin/env python3
"""
小说知识库同步脚本
基于 Turso + SiliconFlow API 的混合存储方案
- Markdown 文件作为原文存储（主存储）
- Turso 数据库存储向量索引（用于语义检索）
"""

import os
import sys
import json
import struct
import hashlib
import requests
import turso
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

# ============ 配置 ============
API_URL = "https://api.siliconflow.cn/v1/embeddings"
API_TOKEN = os.getenv("SILICONFLOW_API_TOKEN", "")
MODEL = "BAAI/bge-m3"
VECTOR_DIM = 1024

# 默认配置
DEFAULT_CONFIG = {
    "chunk_size": 500,
    "chunk_overlap": 100,
    "db_path": ".novel/vector-index/novel_kb.db",
    "content_dirs": ["00-选题", "01-世界观", "02-角色", "03-大纲",
                    "04-分卷", "05-故事线", "06-章纲", "07-正文"]
}


# ============ 数据类 ============
@dataclass
class TextChunk:
    """文本块"""
    id: str
    file_path: str
    heading: str
    content: str
    chunk_index: int
    total_chunks: int
    char_start: int
    char_end: int
    content_type: str


@dataclass
class SearchResult:
    """搜索结果"""
    file_path: str
    heading: str
    content_preview: str
    content_full: str
    similarity: float
    content_type: str


# ============ 向量操作 ============
def get_embedding(text: str) -> List[float]:
    """调用 SiliconFlow API 生成文本向量"""
    if not API_TOKEN:
        raise ValueError("未设置 SILICONFLOW_API_TOKEN 环境变量")

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }
    data = {"model": MODEL, "input": text}

    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        embedding = result["data"][0]["embedding"]

        if len(embedding) != VECTOR_DIM:
            raise ValueError(f"向量维度不匹配: 期望 {VECTOR_DIM}, 实际 {len(embedding)}")

        return embedding
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"API 调用失败: {e}")


def list_to_f32_blob(vector: List[float]) -> bytes:
    """将 float list 转换为 F32 BLOB"""
    return struct.pack(f"{len(vector)}f", *vector)


def f32_blob_to_list(blob: bytes) -> List[float]:
    """将 F32 BLOB 转换回 float list"""
    count = len(blob) // 4
    return list(struct.unpack(f"{count}f", blob))


# ============ 数据库操作 ============
def get_db_path() -> str:
    """获取数据库路径"""
    novel_dir = find_novel_root()
    if novel_dir:
        return os.path.join(novel_dir, DEFAULT_CONFIG["db_path"])
    return DEFAULT_CONFIG["db_path"]


def find_novel_root() -> Optional[str]:
    """查找小说项目根目录（向上查找包含 .novel 目录的目录）"""
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        if (parent / ".novel").exists():
            return str(parent)
    return None


def get_connection():
    """获取数据库连接"""
    db_path = get_db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return turso.connect(db_path)


def init_turso_db() -> None:
    """初始化 Turso 数据库表结构"""
    con = get_connection()
    cur = con.cursor()

    # 创建文件表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS kb_files (
            file_path TEXT PRIMARY KEY,
            content_hash TEXT NOT NULL,
            content_type TEXT NOT NULL,
            modified_time TEXT NOT NULL,
            indexed_at TEXT NOT NULL
        )
    """)

    # 创建文本块表（带向量）
    cur.execute("""
        CREATE TABLE IF NOT EXISTS kb_chunks (
            chunk_id TEXT PRIMARY KEY,
            file_path TEXT NOT NULL,
            heading TEXT,
            content TEXT NOT NULL,
            content_vector F32_BLOB(1024) NOT NULL,
            chunk_index INTEGER NOT NULL,
            total_chunks INTEGER NOT NULL,
            char_start INTEGER NOT NULL,
            char_end INTEGER NOT NULL,
            content_type TEXT NOT NULL,
            indexed_at TEXT NOT NULL,
            FOREIGN KEY (file_path) REFERENCES kb_files(file_path)
        )
    """)

    # 创建向量索引
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_kb_chunks_vector
        ON kb_chunks(libsql_vector_idx(content_vector))
    """)

    # 创建文件路径索引
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_kb_chunks_file
        ON kb_chunks(file_path)
    """)

    con.commit()
    con.close()
    print("数据库初始化完成")


# ============ 文本处理 ============
def detect_content_type(file_path: str) -> str:
    """根据文件路径检测内容类型"""
    path_lower = file_path.lower()
    for content_type in ["世界观", "角色", "大纲", "分卷", "故事线", "章纲", "正文", "选题"]:
        if content_type in path_lower:
            return content_type
    return "other"


def parse_markdown_headings(content: str) -> List[Tuple[str, str, int]]:
    """
    解析 Markdown 标题
    返回: [(heading_text, section_content, start_pos), ...]
    """
    import re

    # 匹配标题行
    heading_pattern = r'^(#{1,3})\s+(.+)$'
    lines = content.split('\n')

    sections = []
    current_heading = "无标题"
    current_content = []
    current_start = 0
    char_pos = 0

    for i, line in enumerate(lines):
        match = re.match(heading_pattern, line)
        if match:
            # 保存上一节
            if current_content:
                sections.append((
                    current_heading,
                    '\n'.join(current_content),
                    current_start
                ))
            # 开始新节
            current_heading = match.group(2).strip()
            current_content = [line]
            current_start = char_pos
        else:
            current_content.append(line)

        char_pos += len(line) + 1  # +1 for newline

    # 保存最后一节
    if current_content:
        sections.append((
            current_heading,
            '\n'.join(current_content),
            current_start
        ))

    return sections if sections else [("无标题", content, 0)]


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[Tuple[str, int, int]]:
    """
    将文本分块
    返回: [(chunk_text, start_pos, end_pos), ...]
    """
    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))

        # 如果不是结尾，尝试在句子边界分割
        if end < len(text):
            # 查找最近的句号、问号、感叹号或换行
            for delimiter in ['。', '？', '！', '. ', '? ', '! ', '\n\n']:
                pos = text.rfind(delimiter, start, end)
                if pos != -1:
                    end = pos + len(delimiter)
                    break

        chunk_text_content = text[start:end].strip()
        if chunk_text_content:
            chunks.append((chunk_text_content, start, end))

        # 下一区块起始位置（带重叠）
        start = end - overlap if end < len(text) else end

    return chunks


def process_markdown_file(file_path: str) -> List[TextChunk]:
    """处理 Markdown 文件，返回文本块列表"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    content_type = detect_content_type(file_path)
    sections = parse_markdown_headings(content)

    chunks = []
    chunk_index = 0

    for heading, section_content, section_start in sections:
        section_chunks = chunk_text(
            section_content,
            DEFAULT_CONFIG["chunk_size"],
            DEFAULT_CONFIG["chunk_overlap"]
        )

        for chunk_text_content, chunk_start, chunk_end in section_chunks:
            chunk_id = hashlib.md5(
                f"{file_path}:{heading}:{chunk_index}".encode()
            ).hexdigest()[:16]

            chunks.append(TextChunk(
                id=chunk_id,
                file_path=file_path,
                heading=heading,
                content=chunk_text_content,
                chunk_index=chunk_index,
                total_chunks=len(section_chunks),
                char_start=section_start + chunk_start,
                char_end=section_start + chunk_end,
                content_type=content_type
            ))
            chunk_index += 1

    return chunks


# ============ 同步逻辑 ============
def compute_file_hash(file_path: str) -> str:
    """计算文件内容的 MD5 哈希"""
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def get_indexed_files() -> Dict[str, Tuple[str, str]]:
    """获取已索引的文件列表 {file_path: (content_hash, indexed_at)}"""
    con = get_connection()
    cur = con.cursor()

    cur.execute("SELECT file_path, content_hash, indexed_at FROM kb_files")
    results = cur.fetchall()

    con.close()
    return {row[0]: (row[1], row[2]) for row in results}


def find_markdown_files(project_dir: str) -> List[str]:
    """查找项目中的所有 Markdown 文件"""
    md_files = []

    for content_dir in DEFAULT_CONFIG["content_dirs"]:
        dir_path = os.path.join(project_dir, content_dir)
        if os.path.exists(dir_path):
            for root, _, files in os.walk(dir_path):
                for file in files:
                    if file.endswith('.md'):
                        md_files.append(os.path.join(root, file))

    return md_files


def index_file(file_path: str, content_type: str = None) -> int:
    """索引单个文件到知识库"""
    print(f"  索引: {file_path}")

    chunks = process_markdown_file(file_path)
    if not chunks:
        return 0

    content_hash = compute_file_hash(file_path)
    indexed_at = datetime.now().isoformat()

    con = get_connection()
    cur = con.cursor()

    # 插入/更新文件记录
    if content_type is None:
        content_type = detect_content_type(file_path)

    cur.execute("""
        INSERT OR REPLACE INTO kb_files (file_path, content_hash, content_type, modified_time, indexed_at)
        VALUES (?, ?, ?, ?, ?)
    """, (file_path, content_hash, content_type,
          datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
          indexed_at))

    # 删除旧块
    cur.execute("DELETE FROM kb_chunks WHERE file_path = ?", (file_path,))

    # 插入新块（带向量）
    for chunk in chunks:
        try:
            embedding = get_embedding(chunk.content)
            vector_blob = list_to_f32_blob(embedding)

            cur.execute("""
                INSERT INTO kb_chunks
                (chunk_id, file_path, heading, content, content_vector,
                 chunk_index, total_chunks, char_start, char_end, content_type, indexed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (chunk.id, chunk.file_path, chunk.heading, chunk.content, vector_blob,
                  chunk.chunk_index, chunk.total_chunks, chunk.char_start, chunk.char_end,
                  chunk.content_type, indexed_at))
        except Exception as e:
            print(f"    警告: 块 {chunk.id} 向量生成失败: {e}")
            continue

    con.commit()
    con.close()

    return len(chunks)


def remove_file_from_index(file_path: str) -> None:
    """从索引中移除文件"""
    con = get_connection()
    cur = con.cursor()

    cur.execute("DELETE FROM kb_chunks WHERE file_path = ?", (file_path,))
    cur.execute("DELETE FROM kb_files WHERE file_path = ?", (file_path,))

    con.commit()
    con.close()
    print(f"  已移除: {file_path}")


def sync_knowledge_base(full_rebuild: bool = False) -> Dict[str, Any]:
    """
    同步知识库
    - 增量模式: 只处理新增或修改的文件
    - 全量模式: 重建整个索引
    """
    project_dir = find_novel_root()
    if not project_dir:
        raise RuntimeError("未找到小说项目根目录（缺少 .novel 目录）")

    print(f"项目目录: {project_dir}")
    print(f"同步模式: {'全量重建' if full_rebuild else '增量更新'}")
    print()

    # 初始化数据库
    init_turso_db()

    # 获取当前 Markdown 文件
    current_files = set(find_markdown_files(project_dir))

    if full_rebuild:
        # 全量模式：清空并重建
        con = get_connection()
        cur = con.cursor()
        cur.execute("DELETE FROM kb_chunks")
        cur.execute("DELETE FROM kb_files")
        con.commit()
        con.close()
        indexed_files = {}
    else:
        indexed_files = get_indexed_files()

    # 找出变更
    indexed_paths = set(indexed_files.keys())
    to_add = current_files - indexed_paths
    to_remove = indexed_paths - current_files
    to_update = set()

    if not full_rebuild:
        for path in current_files & indexed_paths:
            if os.path.exists(path):
                current_hash = compute_file_hash(path)
                if current_hash != indexed_files[path][0]:
                    to_update.add(path)

    print(f"新增文件: {len(to_add)}")
    print(f"修改文件: {len(to_update)}")
    print(f"删除文件: {len(to_remove)}")
    print(f"未变更: {len(current_files - to_add - to_update)}")
    print()

    stats = {"added": 0, "updated": 0, "removed": 0, "chunks": 0}

    # 处理删除
    for file_path in to_remove:
        remove_file_from_index(file_path)
        stats["removed"] += 1

    # 处理新增和更新
    for file_path in to_add | to_update:
        try:
            chunk_count = index_file(file_path)
            stats["chunks"] += chunk_count
            if file_path in to_add:
                stats["added"] += 1
            else:
                stats["updated"] += 1
        except Exception as e:
            print(f"  错误: 索引失败: {e}")

    print()
    print("=" * 50)
    print(f"同步完成!")
    print(f"  新增: {stats['added']} 个文件")
    print(f"  更新: {stats['updated']} 个文件")
    print(f"  删除: {stats['removed']} 个文件")
    print(f"  总块数: {stats['chunks']} 个")

    return stats


# ============ 搜索功能 ============
def search_knowledge(
    query: str,
    limit: int = 5,
    content_type: str = None,
    threshold: float = 0.0
) -> List[SearchResult]:
    """
    语义搜索知识库

    Args:
        query: 搜索查询
        limit: 返回结果数量
        content_type: 按内容类型过滤（如"角色"、"世界观"）
        threshold: 相似度阈值（0-1），低于此值的结果会被过滤

    Returns:
        搜索结果列表
    """
    print(f"正在搜索: '{query}'")

    # 生成查询向量
    query_embedding = get_embedding(query)
    query_vector_blob = list_to_f32_blob(query_embedding)

    con = get_connection()
    cur = con.cursor()

    # 构建查询
    if content_type:
        sql = """
            SELECT file_path, heading, content,
                   vector_distance_cos(content_vector, ?) as distance
            FROM kb_chunks
            WHERE content_type = ?
            ORDER BY distance ASC
            LIMIT ?
        """
        params = (query_vector_blob, content_type, limit * 2)
    else:
        sql = """
            SELECT file_path, heading, content,
                   vector_distance_cos(content_vector, ?) as distance
            FROM kb_chunks
            ORDER BY distance ASC
            LIMIT ?
        """
        params = (query_vector_blob, limit * 2)

    cur.execute(sql, params)
    rows = cur.fetchall()
    con.close()

    results = []
    for row in rows:
        file_path, heading, content, distance = row
        similarity = 1.0 - distance  # 距离转相似度

        if similarity >= threshold:
            # 读取完整内容
            full_content = ""
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    full_content = f.read()
            except Exception:
                pass

            results.append(SearchResult(
                file_path=file_path,
                heading=heading,
                content_preview=content[:200] + "..." if len(content) > 200 else content,
                content_full=full_content,
                similarity=similarity,
                content_type=detect_content_type(file_path)
            ))

    return results[:limit]


def search_to_markdown(results: List[SearchResult]) -> str:
    """将搜索结果转换为 Markdown 格式"""
    if not results:
        return "未找到相关结果。"

    lines = ["# 知识库搜索结果\n"]

    for i, result in enumerate(results, 1):
        lines.append(f"## [{i}] {result.heading}")
        lines.append(f"- **文件**: `{result.file_path}`")
        lines.append(f"- **类型**: {result.content_type}")
        lines.append(f"- **相关度**: {result.similarity:.2%}")
        lines.append("")
        lines.append("### 内容预览")
        lines.append(result.content_preview)
        lines.append("")
        lines.append("### 完整内容")
        lines.append("```markdown")
        lines.append(result.content_full[:2000] if len(result.content_full) > 2000 else result.content_full)
        if len(result.content_full) > 2000:
            lines.append("\n... (内容已截断)")
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


# ============ 命令行接口 ============
def main():
    import argparse

    parser = argparse.ArgumentParser(description="小说知识库同步工具")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # init 命令
    init_parser = subparsers.add_parser("init", help="初始化数据库")

    # sync 命令
    sync_parser = subparsers.add_parser("sync", help="同步知识库")
    sync_parser.add_argument(
        "--full", "-f",
        action="store_true",
        help="全量重建（默认增量更新）"
    )

    # search 命令
    search_parser = subparsers.add_parser("search", help="搜索知识库")
    search_parser.add_argument("query", help="搜索查询")
    search_parser.add_argument(
        "-n", "--limit",
        type=int,
        default=5,
        help="返回结果数量（默认5）"
    )
    search_parser.add_argument(
        "-t", "--type",
        help="按内容类型过滤（如：角色、世界观、大纲）"
    )
    search_parser.add_argument(
        "--threshold",
        type=float,
        default=0.0,
        help="相似度阈值（0-1，默认0）"
    )
    search_parser.add_argument(
        "-o", "--output",
        help="输出结果到文件"
    )

    # stats 命令
    stats_parser = subparsers.add_parser("stats", help="显示统计信息")

    args = parser.parse_args()

    if args.command == "init":
        init_turso_db()
        print("数据库初始化完成")

    elif args.command == "sync":
        try:
            stats = sync_knowledge_base(full_rebuild=args.full)
            print(json.dumps(stats, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"同步失败: {e}")
            sys.exit(1)

    elif args.command == "search":
        try:
            results = search_knowledge(
                query=args.query,
                limit=args.limit,
                content_type=args.type,
                threshold=args.threshold
            )

            markdown_output = search_to_markdown(results)

            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(markdown_output)
                print(f"搜索结果已保存到: {args.output}")
            else:
                print(markdown_output)

        except Exception as e:
            print(f"搜索失败: {e}")
            sys.exit(1)

    elif args.command == "stats":
        con = get_connection()
        cur = con.cursor()

        cur.execute("SELECT COUNT(*) FROM kb_files")
        file_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM kb_chunks")
        chunk_count = cur.fetchone()[0]

        cur.execute("SELECT content_type, COUNT(*) FROM kb_files GROUP BY content_type")
        type_stats = cur.fetchall()

        con.close()

        print("=" * 50)
        print("知识库统计")
        print("=" * 50)
        print(f"索引文件数: {file_count}")
        print(f"文本块数: {chunk_count}")
        print()
        print("按类型分布:")
        for content_type, count in type_stats:
            print(f"  {content_type}: {count}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
