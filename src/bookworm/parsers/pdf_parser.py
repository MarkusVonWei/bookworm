import re
from pathlib import Path
from typing import List, Optional

from PyPDF2 import PdfReader

from .base import BookParser, BookMetadata, Chapter, ParsedBook


class PDFParser(BookParser):
    """PDF解析器"""

    def parse(self) -> ParsedBook:
        """解析PDF文件"""
        reader = PdfReader(str(self.file_path))
        
        # 获取元数据
        metadata = self.get_metadata()
        
        # 获取章节
        chapters = self.get_chapters()
        
        # 获取完整文本
        full_text = self.get_full_text()
        
        return ParsedBook(
            metadata=metadata,
            chapters=chapters,
            full_text=full_text,
            total_pages=len(reader.pages)
        )

    def get_metadata(self) -> BookMetadata:
        """获取PDF元数据"""
        reader = PdfReader(str(self.file_path))
        info = reader.metadata
        
        title = "Unknown"
        author = None
        publisher = None
        year = None
        
        if info:
            title = info.title or self.file_path.stem
            author = info.author
            publisher = info.producer
            if info.creation_date:
                year = info.creation_date.year
        
        return BookMetadata(
            title=title,
            author=author,
            publisher=publisher,
            year=year,
            file_path=str(self.file_path),
            file_size=self.file_path.stat().st_size
        )

    def get_chapters(self) -> List[Chapter]:
        """从PDF提取章节"""
        reader = PdfReader(str(self.file_path))
        chapters = []
        
        current_chapter_title = "前言"
        current_chapter_content = []
        chapter_index = 0
        
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if not text:
                continue
            
            # 检测章节标题
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 检测章节标题模式
                if self._is_chapter_title(line):
                    # 保存当前章节
                    if current_chapter_content:
                        chapter_content = '\n'.join(current_chapter_content)
                        chapters.append(Chapter(
                            title=current_chapter_title,
                            content=chapter_content,
                            index=chapter_index,
                            start_page=page_num if chapter_index == 0 else None,
                            end_page=page_num
                        ))
                        chapter_index += 1
                    
                    current_chapter_title = line
                    current_chapter_content = []
                else:
                    current_chapter_content.append(line)
        
        # 保存最后一个章节
        if current_chapter_content:
            chapter_content = '\n'.join(current_chapter_content)
            chapters.append(Chapter(
                title=current_chapter_title,
                content=chapter_content,
                index=chapter_index,
                start_page=len(reader.pages) - 1,
                end_page=len(reader.pages) - 1
            ))
        
        return chapters

    def get_full_text(self) -> str:
        """获取PDF完整文本"""
        reader = PdfReader(str(self.file_path))
        texts = []
        
        for page in reader.pages:
            text = page.extract_text()
            if text:
                texts.append(text)
        
        return self._clean_text('\n\n'.join(texts))

    def _is_chapter_title(self, line: str) -> bool:
        """检测是否为章节标题"""
        # 常见的章节标题模式
        patterns = [
            r'^第[一二三四五六七八九十百千\d]+[章节篇]',
            r'^Chapter\s+\d+',
            r'^CHAPTER\s+\d+',
            r'^\d+\.\s+[A-Z]',
            r'^[IVXLC]+\.\s+',
        ]
        
        for pattern in patterns:
            if re.match(pattern, line, re.IGNORECASE):
                return True
        
        # 如果行长度较短且全大写或首字母大写，可能是标题
        if len(line) < 100:
            if line.isupper() or (line[0].isupper() and not line.endswith('.')):
                return True
        
        return False