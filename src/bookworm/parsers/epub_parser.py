import re
import logging
from pathlib import Path
from typing import List

import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

from .base import BookParser, BookMetadata, Chapter, ParsedBook

# 配置日志
logger = logging.getLogger("bookworm")


class EPUBParser(BookParser):
    """EPUB解析器"""

    def parse(self) -> ParsedBook:
        """解析EPUB文件"""
        logger.info(f"开始解析EPUB文件: {self.file_path}")
        
        try:
            metadata = self.get_metadata()
            logger.info(f"获取元数据成功: {metadata.title}")
            
            chapters = self.get_chapters()
            logger.info(f"提取章节数量: {len(chapters)}")
            
            full_text = self.get_full_text()
            logger.info(f"提取全文长度: {len(full_text)} 字符")
            
            return ParsedBook(
                metadata=metadata,
                chapters=chapters,
                full_text=full_text
            )
        except Exception as e:
            logger.error(f"EPUB解析失败: {str(e)}", exc_info=True)
            raise

    def get_metadata(self) -> BookMetadata:
        """获取EPUB元数据"""
        book = epub.read_epub(str(self.file_path))
        
        title = book.get_metadata('DC', 'title')
        title = title[0][0] if title else self.file_path.stem
        
        author = book.get_metadata('DC', 'creator')
        author = author[0][0] if author else None
        
        publisher = book.get_metadata('DC', 'publisher')
        publisher = publisher[0][0] if publisher else None
        
        year = None
        date = book.get_metadata('DC', 'date')
        if date:
            try:
                year = int(date[0][0][:4])
            except (ValueError, IndexError):
                pass
        
        language = book.get_metadata('DC', 'language')
        language = language[0][0] if language else "en"
        
        return BookMetadata(
            title=title,
            author=author,
            publisher=publisher,
            year=year,
            language=language,
            file_path=str(self.file_path),
            file_size=self.file_path.stat().st_size
        )

    def get_chapters(self) -> List[Chapter]:
        """从EPUB提取章节"""
        logger.info(f"开始提取EPUB章节: {self.file_path}")
        
        try:
            book = epub.read_epub(str(self.file_path))
            chapters = []
            
            # 获取目录
            toc = book.toc
            logger.info(f"目录项数量: {len(toc)}")
            
            # 获取所有文档项
            items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
            logger.info(f"文档项数量: {len(items)}")
            
            chapter_index = 0
            for item in items:
                try:
                    content = item.get_content().decode('utf-8')
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # 提取文本
                    text = soup.get_text()
                    if not text.strip():
                        continue
                    
                    # 尝试从内容中提取标题
                    title = self._extract_title(soup)
                    if not title:
                        title = f"章节 {chapter_index + 1}"
                    
                    chapters.append(Chapter(
                        title=title,
                        content=text.strip(),
                        index=chapter_index
                    ))
                    chapter_index += 1
                    
                except Exception as e:
                    logger.warning(f"处理文档项失败: {str(e)}")
                    continue
            
            logger.info(f"成功提取 {len(chapters)} 个章节")
            return chapters
            
        except Exception as e:
            logger.error(f"提取EPUB章节失败: {str(e)}", exc_info=True)
            raise

    def get_full_text(self) -> str:
        """获取EPUB完整文本"""
        logger.info(f"开始提取EPUB全文: {self.file_path}")
        
        try:
            book = epub.read_epub(str(self.file_path))
            texts = []
            
            for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
                try:
                    content = item.get_content().decode('utf-8')
                    soup = BeautifulSoup(content, 'html.parser')
                    text = soup.get_text()
                    if text.strip():
                        texts.append(text.strip())
                except Exception as e:
                    logger.warning(f"处理文档项失败: {str(e)}")
                    continue
            
            full_text = self._clean_text('\n\n'.join(texts))
            logger.info(f"全文提取完成，长度: {len(full_text)} 字符")
            
            return full_text
            
        except Exception as e:
            logger.error(f"提取EPUB全文失败: {str(e)}", exc_info=True)
            raise

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """从HTML中提取标题"""
        # 尝试从h1-h6标签提取
        for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            title_tag = soup.find(tag)
            if title_tag:
                return title_tag.get_text().strip()
        
        # 尝试从title标签提取
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        
        return ""