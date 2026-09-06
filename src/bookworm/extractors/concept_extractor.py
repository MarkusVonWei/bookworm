import json
import logging
from typing import List, Optional
from dataclasses import dataclass

from ..utils import get_llm_client

logger = logging.getLogger("bookworm")


@dataclass
class Concept:
    """概念数据类"""
    name: str
    definition: str
    context: str
    importance: float  # 0-1之间
    occurrences: List[str]  # 出现位置


class ConceptExtractor:
    """核心概念提取器"""

    def __init__(self, llm=None):
        self.llm = llm or get_llm_client()
        self.extraction_prompt = """
        你是一个专业的书籍分析专家。请从以下文本中提取核心概念。

        要求：
        1. 识别文本中的关键术语、重要概念和专业词汇
        2. 为每个概念提供清晰的定义
        3. 标注概念的重要性（0-1之间，1表示最重要）
        4. 记录概念出现的上下文

        文本内容：
        {text}

        请以JSON格式返回结果，格式如下：
        {{
            "concepts": [
                {{
                    "name": "概念名称",
                    "definition": "概念定义",
                    "context": "概念出现的上下文",
                    "importance": 0.8
                }}
            ]
        }}

        只返回JSON，不要有其他内容。
        """

    def extract(self, text: str, max_concepts: int = 20) -> List[Concept]:
        """从文本中提取核心概念"""
        # 如果文本太长，分块处理
        if len(text) > 4000:
            return self._extract_from_long_text(text, max_concepts)
        
        prompt = self.extraction_prompt.format(text=text)
        
        try:
            logger.debug(f"开始概念提取, 文本长度: {len(text)}")
            response = self.llm.complete(prompt)
            result = json.loads(response.text)
            
            concepts = []
            for item in result.get("concepts", [])[:max_concepts]:
                concepts.append(Concept(
                    name=item["name"],
                    definition=item["definition"],
                    context=item["context"],
                    importance=item.get("importance", 0.5),
                    occurrences=[item["context"]]
                ))
            
            logger.info(f"概念提取成功, 提取到 {len(concepts)} 个概念")
            return concepts
        except Exception as e:
            logger.error(f"概念提取失败: {e}", exc_info=True)
            return []

    def _extract_from_long_text(self, text: str, max_concepts: int) -> List[Concept]:
        """从长文本中提取概念"""
        # 将文本分成多个块
        chunk_size = 3000
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
        all_concepts = []
        seen_names = set()
        
        for chunk in chunks:
            concepts = self.extract(chunk, max_concepts=max_concepts)
            for concept in concepts:
                if concept.name not in seen_names:
                    all_concepts.append(concept)
                    seen_names.add(concept.name)
        
        # 按重要性排序
        all_concepts.sort(key=lambda x: x.importance, reverse=True)
        
        return all_concepts[:max_concepts]

    def extract_from_chapters(self, chapters: List[dict]) -> List[Concept]:
        """从多个章节中提取概念"""
        all_concepts = []
        seen_names = set()
        
        for chapter in chapters:
            text = chapter.get("content", "")
            concepts = self.extract(text)
            
            for concept in concepts:
                if concept.name not in seen_names:
                    all_concepts.append(concept)
                    seen_names.add(concept.name)
                else:
                    # 更新已存在概念的出现位置
                    for existing in all_concepts:
                        if existing.name == concept.name:
                            existing.occurrences.extend(concept.occurrences)
                            break
        
        # 按重要性排序
        all_concepts.sort(key=lambda x: x.importance, reverse=True)
        
        return all_concepts