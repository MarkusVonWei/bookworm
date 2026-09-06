from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class BookMetadata:
    """书籍元数据"""
    title: str
    author: Optional[str] = None
    publisher: Optional[str] = None
    year: Optional[int] = None
    isbn: Optional[str] = None
    language: str = "en"
    file_path: str = ""
    file_size: int = 0


@dataclass
class Chapter:
    """章节信息"""
    title: str
    content: str
    index: int
    start_page: Optional[int] = None
    end_page: Optional[int] = None


@dataclass
class ParsedBook:
    """解析后的书籍"""
    metadata: BookMetadata
    chapters: List[Chapter]
    full_text: str
    total_pages: Optional[int] = None


class BookParser(ABC):
    """书籍解析器基类"""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

    @abstractmethod
    def parse(self) -> ParsedBook:
        """解析书籍，返回解析结果"""
        pass

    @abstractmethod
    def get_metadata(self) -> BookMetadata:
        """获取书籍元数据"""
        pass

    @abstractmethod
    def get_chapters(self) -> List[Chapter]:
        """获取章节列表"""
        pass

    @abstractmethod
    def get_full_text(self) -> str:
        """获取完整文本"""
        pass

    def _clean_text(self, text: str) -> str:
        """清洗文本，去除多余空白"""
        import re
        # 去除多余空白行
        text = re.sub(r'\n\s*\n', '\n\n', text)
        # 去除行首尾空白
        lines = [line.strip() for line in text.split('\n')]
        return '\n'.join(lines)