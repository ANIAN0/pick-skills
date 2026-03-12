#!/usr/bin/env python3
"""
Markdown 解析器 - 将 Markdown 文件解析为结构化数据
用于 md-to-visual skill
"""

import re
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Optional


@dataclass
class ContentBlock:
    """内容块"""
    type: str  # 'heading', 'paragraph', 'list', 'image', 'quote', 'divider'
    content: str
    level: int = 0  # 用于标题层级
    items: List[str] = None  # 用于列表项


@dataclass
class ParsedArticle:
    """解析后的文章"""
    title: str
    blocks: List[ContentBlock]
    images: List[str]


def parse_markdown(md_content: str) -> ParsedArticle:
    """解析 Markdown 内容为结构化数据"""
    blocks = []
    images = []
    title = ""

    # 按行分割并处理
    lines = md_content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # 跳过空行
        if not line:
            i += 1
            continue

        # 标题 (H1-H6)
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if heading_match:
            level = len(heading_match.group(1))
            content = heading_match.group(2)
            blocks.append(ContentBlock(
                type='heading',
                content=content,
                level=level
            ))
            if level == 1 and not title:
                title = content
            i += 1
            continue

        # 分隔线
        if line == '---' or line == '***' or line == '___':
            blocks.append(ContentBlock(type='divider', content=''))
            i += 1
            continue

        # 图片 - Obsidian 格式: ![[filename.png]]
        obsidian_img = re.findall(r'!\[\[(.+?)\]\]', line)
        if obsidian_img:
            for img in obsidian_img:
                blocks.append(ContentBlock(type='image', content=img))
                images.append(img)
            i += 1
            continue

        # 图片 - 标准 Markdown 格式: ![alt](path)
        standard_img = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', line)
        if standard_img:
            for alt, path in standard_img:
                blocks.append(ContentBlock(type='image', content=path))
                images.append(path)
            i += 1
            continue

        # 引用块
        if line.startswith('>'):
            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith('>'):
                quote_lines.append(lines[i].strip()[1:].strip())
                i += 1
            blocks.append(ContentBlock(
                type='quote',
                content='\n'.join(quote_lines)
            ))
            continue

        # 列表
        if re.match(r'^[\s]*[-*+][\s]', line):
            list_items = []
            while i < len(lines):
                list_match = re.match(r'^[\s]*[-*+][\s]+(.+)$', lines[i])
                if list_match:
                    list_items.append(list_match.group(1))
                    i += 1
                elif lines[i].strip() == '' and i + 1 < len(lines) and re.match(r'^[\s]*[-*+][\s]', lines[i + 1]):
                    i += 1
                else:
                    break
            blocks.append(ContentBlock(
                type='list',
                content='',
                items=list_items
            ))
            continue

        # 段落（收集多行直到空行）
        paragraph_lines = [line]
        i += 1
        while i < len(lines):
            next_line = lines[i]
            # 遇到空行或新块开始，结束段落
            if not next_line.strip() or next_line.strip().startswith('#') or \
               next_line.strip().startswith('>') or next_line.strip().startswith('-') or \
               next_line.strip().startswith('*') or next_line.strip() == '---':
                break
            paragraph_lines.append(next_line)
            i += 1

        paragraph_text = ' '.join(paragraph_lines).strip()
        if paragraph_text:
            blocks.append(ContentBlock(type='paragraph', content=paragraph_text))

    # 如果没有找到 H1，使用第一行作为标题
    if not title and blocks:
        for block in blocks:
            if block.type in ['paragraph', 'heading']:
                title = block.content[:50]
                break

    return ParsedArticle(title=title, blocks=blocks, images=images)


def paginate_content(blocks: List[ContentBlock], max_chars_per_page: int = 250) -> List[List[ContentBlock]]:
    """
    将内容分页
    - 封面：H1 标题 + 摘要
    - 内容页：按章节或字数分页
    """
    pages = []
    current_page = []
    current_chars = 0
    has_cover = False

    for block in blocks:
        # H1 标题创建封面
        if block.type == 'heading' and block.level == 1 and not has_cover:
            if current_page:
                pages.append(current_page)
            cover_blocks = [block]
            # 添加接下来的段落作为摘要
            next_idx = blocks.index(block) + 1
            abstract_chars = 0
            while next_idx < len(blocks) and abstract_chars < 150:
                next_block = blocks[next_idx]
                if next_block.type == 'paragraph':
                    cover_blocks.append(next_block)
                    abstract_chars += len(next_block.content)
                next_idx += 1
            pages.append(cover_blocks)
            has_cover = True
            current_page = []
            current_chars = 0
            continue

        # 分隔线强制分页
        if block.type == 'divider':
            if current_page:
                pages.append(current_page)
                current_page = []
                current_chars = 0
            continue

        # H2/H3 标题在新页面开始（如果当前页已有内容）
        if block.type == 'heading' and block.level >= 2 and current_page:
            if current_chars > 100:  # 当前页已有足够内容
                pages.append(current_page)
                current_page = [block]
                current_chars = len(block.content)
                continue

        # 计算内容长度
        content_len = len(block.content)
        if block.items:
            content_len += sum(len(item) for item in block.items)

        # 如果超出单页限制，保存当前页
        if current_chars + content_len > max_chars_per_page and current_page:
            pages.append(current_page)
            current_page = [block]
            current_chars = content_len
        else:
            current_page.append(block)
            current_chars += content_len

    # 添加最后一页
    if current_page:
        pages.append(current_page)

    return pages


def main():
    """命令行入口"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python parse_md.py <markdown_file>")
        sys.exit(1)

    md_path = Path(sys.argv[1])
    if not md_path.exists():
        print(f"Error: File not found: {md_path}")
        sys.exit(1)

    # 读取并解析
    content = md_path.read_text(encoding='utf-8')
    article = parse_markdown(content)
    pages = paginate_content(article.blocks)

    # 输出 JSON
    result = {
        "title": article.title,
        "images": article.images,
        "total_pages": len(pages),
        "pages": [
            {
                "page_number": i + 1,
                "blocks": [asdict(b) for b in page]
            }
            for i, page in enumerate(pages)
        ]
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
