#!/usr/bin/env python3
"""
小说知识库同步模块

基于 Turso + SiliconFlow API 的混合存储方案
- Markdown 文件作为原文存储（主存储）
- Turso 数据库存储向量索引（用于语义检索）
"""

from .kb_sync import (
    get_embedding,
    list_to_f32_blob,
    init_turso_db,
    sync_knowledge_base,
    search_knowledge,
    get_stats,
    TextChunk,
    SearchResult,
)

__all__ = [
    "get_embedding",
    "list_to_f32_blob",
    "init_turso_db",
    "sync_knowledge_base",
    "search_knowledge",
    "get_stats",
    "TextChunk",
    "SearchResult",
]
