import re
from pathlib import Path
from typing import List

from .base import BookParser, BookMetadata, Chapter, ParsedBook


class TXTParser(BookParser):
    """TXT解析器"""

    def parse(self) -> ParsedBook:
        """解析TXT文件"""
        metadata = self.get_metadata()
        chapters = self.get_chapters()
        full_text = self.get_full_text()
        
        return ParsedBook(
            metadata=metadata,
            chapters=chapters,
            full_text=full_text
        )

    def get_metadata(self) -> BookMetadata:
        """获取TXT元数据"""
        return BookMetadata(
            title=self.file_path.stem,
            file_path=str(self.file_path),
            file_size=self.file_path.stat().st_size
        )

    def get_chapters(self) -> List[Chapter]:
        """从TXT提取章节"""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        chapters = []
        current_chapter_title = "前言"
        current_chapter_content = []
        chapter_index = 0
        
        lines = content.split('\n')
        
        for line in lines:
            line_stripped = line.strip()
            
            # 检测章节标题
            if self._is_chapter_title(line_stripped):
                # 保存当前章节
                if current_chapter_content:
                    chapter_content = '\n'.join(current_chapter_content)
                    chapters.append(Chapter(
                        title=current_chapter_title,
                        content=chapter_content,
                        index=chapter_index
                    ))
                    chapter_index += 1
                
                current_chapter_title = line_stripped
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
        """获取TXT完整文本"""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return self._clean_text(content)

    def _is_chapter_title(self, line: str) -> bool:
        """检测是否为章节标题"""
        if not line:
            return False
        
        # 常见的章节标题模式
        patterns = [
            r'^第[一二三四五六七八九十百千\d]+[章节篇]',
            r'^Chapter\s+\d+',
            r'^CHAPTER\s+\d+',
            r'^\d+\.\s+[A-Z]',
            r'^[IVXLC]+\.\s+',
            r'^【.*】$',
            r'^=.*=$',
            r'^\*{3,}$',
            r'^-{3,}$',
        ]
        
        for pattern in patterns:
            if re.match(pattern, line, re.IGNORECASE):
                return True
        
        # 如果行长度较短且全大写，可能是标题
        if len(line) < 50 and line.isupper():
            return True
        
        return False