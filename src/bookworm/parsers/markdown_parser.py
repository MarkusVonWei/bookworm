import re
from pathlib import Path
from typing import List

from .base import BookParser, BookMetadata, Chapter, ParsedBook


class MarkdownParser(BookParser):
    """Markdown解析器"""

    def parse(self) -> ParsedBook:
        """解析Markdown文件"""
        metadata = self.get_metadata()
        chapters = self.get_chapters()
        full_text = self.get_full_text()
        
        return ParsedBook(
            metadata=metadata,
            chapters=chapters,
            full_text=full_text
        )

    def get_metadata(self) -> BookMetadata:
        """获取Markdown元数据"""
        title = self.file_path.stem
        
        # 尝试从文件内容提取标题
        with open(self.file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            if first_line.startswith('#'):
                title = first_line.lstrip('#').strip()
        
        return BookMetadata(
            title=title,
            file_path=str(self.file_path),
            file_size=self.file_path.stat().st_size
        )

    def get_chapters(self) -> List[Chapter]:
        """从Markdown提取章节"""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        chapters = []
        current_chapter_title = "前言"
        current_chapter_content = []
        chapter_index = 0
        
        lines = content.split('\n')
        
        for line in lines:
            # 检测Markdown标题
            if re.match(r'^#{1,6}\s+', line):
                # 保存当前章节
                if current_chapter_content:
                    chapter_content = '\n'.join(current_chapter_content)
                    chapters.append(Chapter(
                        title=current_chapter_title,
                        content=chapter_content,
                        index=chapter_index
                    ))
                    chapter_index += 1
                
                # 提取新标题
                current_chapter_title = line.lstrip('#').strip()
                current_chapter_content = []
            else:
                current_chapter_content.append(line)
        
        # 保存最后一个章节
        if current_chapter_content:
            chapter_content = '\n'.join(current_chapter_content)
            chapters.append(Chapter(
                title=current_chapter_title,
                content=chapter_content,
                index=chapter_index
            ))
        
        return chapters

    def get_full_text(self) -> str:
        """获取Markdown完整文本"""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return self._clean_text(content)