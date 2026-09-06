import logging
from pathlib import Path
from typing import Optional

from .base import BookParser
from .pdf_parser import PDFParser
from .txt_parser import TXTParser
from .epub_parser import EPUBParser
from .markdown_parser import MarkdownParser

# 配置日志
logger = logging.getLogger("bookworm")


def get_parser(file_path: str) -> BookParser:
    """根据文件扩展名获取对应的解析器"""
    path = Path(file_path)
    extension = path.suffix.lower()
    
    logger.info(f"获取解析器，文件: {file_path}, 扩展名: {extension}")
    
    parsers = {
        '.pdf': PDFParser,
        '.txt': TXTParser,
        '.epub': EPUBParser,
        '.md': MarkdownParser,
        '.markdown': MarkdownParser,
    }
    
    parser_class = parsers.get(extension)
    if not parser_class:
        logger.error(f"不支持的文件格式: {extension}")
        raise ValueError(f"不支持的文件格式: {extension}")
    
    logger.info(f"使用解析器: {parser_class.__name__}")
    return parser_class(file_path)


def parse_book(file_path: str):
    """解析书籍的便捷函数"""
    logger.info(f"开始解析书籍: {file_path}")
    
    try:
        parser = get_parser(file_path)
        result = parser.parse()
        logger.info(f"书籍解析成功: {result.metadata.title}")
        return result
    except Exception as e:
        logger.error(f"书籍解析失败: {str(e)}", exc_info=True)
        raise