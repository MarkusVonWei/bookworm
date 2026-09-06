import json
import logging
from typing import List, Optional
from dataclasses import dataclass
from enum import Enum

from ..utils import get_llm_client

logger = logging.getLogger("bookworm")


class RelationType(Enum):
    """关系类型"""
    DEFINES = "DEFINES"  # 定义关系
    SUPPORTS = "SUPPORTS"  # 支持关系
    CONTRADICTS = "CONTRADICTS"  # 反对关系
    CAUSES = "CAUSES"  # 因果关系
    EXEMPLIFIES = "EXEMPLIFIES"  # 举例关系
    RELATES_TO = "RELATES_TO"  # 相关关系
    PART_OF = "PART_OF"  # 部分关系
    SIMILAR_TO = "SIMILAR_TO"  # 相似关系


@dataclass
class Relation:
    """关系数据类"""
    source: str  # 源概念
    target: str  # 目标概念
    relation_type: RelationType  # 关系类型
    strength: float  # 关系强度 (0-1)
    context: str  # 关系上下文


class RelationExtractor:
    """关系提取器"""

    def __init__(self, llm=None):
        self.llm = llm or get_llm_client()
        self.extraction_prompt = """
        你是一个专业的书籍分析专家。请从以下文本中提取概念之间的关系。

        要求：
        1. 识别概念之间的逻辑关系
        2. 关系类型包括：
           - DEFINES: 定义关系（A定义为B）
           - SUPPORTS: 支持关系（A支持B）
           - CONTRADICTS: 反对关系（A反对B）
           - CAUSES: 因果关系（A导致B）
           - EXEMPLIFIES: 举例关系（A是B的例子）
           - RELATES_TO: 相关关系（A与B相关）
           - PART_OF: 部分关系（A是B的一部分）
           - SIMILAR_TO: 相似关系（A与B相似）
        3. 评估关系的强度（0-1之间）
        4. 记录关系出现的上下文

        文本内容：
        {text}

        已知概念列表：
        {concepts}

        请以JSON格式返回结果，格式如下：
        {{
            "relations": [
                {{
                    "source": "源概念",
                    "target": "目标概念",
                    "relation_type": "SUPPORTS",
                    "strength": 0.8,
                    "context": "关系出现的上下文"
                }}
            ]
        }}

        只返回JSON，不要有其他内容。
        """

    def extract(self, text: str, concepts: List[str], max_relations: int = 30) -> List[Relation]:
        """从文本中提取概念关系"""
        # 如果文本太长，分块处理
        if len(text) > 4000:
            return self._extract_from_long_text(text, concepts, max_relations)
        
        concepts_str = "\n".join([f"- {c}" for c in concepts])
        prompt = self.extraction_prompt.format(text=text, concepts=concepts_str)
        
        try:
            logger.debug(f"开始关系提取, 文本长度: {len(text)}, 概念数: {len(concepts)}")
            response = self.llm.complete(prompt)
            result = json.loads(response.text)
            
            relations = []
            for item in result.get("relations", [])[:max_relations]:
                # 验证关系类型
                try:
                    relation_type = RelationType(item["relation_type"])
                except ValueError:
                    relation_type = RelationType.RELATES_TO
                
                relations.append(Relation(
                    source=item["source"],
                    target=item["target"],
                    relation_type=relation_type,
                    strength=item.get("strength", 0.5),
                    context=item.get("context", "")
                ))
            
            logger.info(f"关系提取成功, 提取到 {len(relations)} 条关系")
            return relations
        except Exception as e:
            logger.error(f"关系提取失败: {e}", exc_info=True)
            return []

    def _extract_from_long_text(self, text: str, concepts: List[str], max_relations: int) -> List[Relation]:
        """从长文本中提取关系"""
        # 将文本分成多个块
        chunk_size = 3000
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
        all_relations = []
        seen_relations = set()
        
        for chunk in chunks:
            relations = self.extract(chunk, concepts, max_relations=max_relations)
            for rel in relations:
                # 创建关系的唯一标识
                rel_key = (rel.source, rel.target, rel.relation_type.value)
                if rel_key not in seen_relations:
                    all_relations.append(rel)
                    seen_relations.add(rel_key)
        
        # 按强度排序
        all_relations.sort(key=lambda x: x.strength, reverse=True)
        
        return all_relations[:max_relations]

    def extract_from_chapters(self, chapters: List[dict], concepts: List[str]) -> List[Relation]:
        """从多个章节中提取关系"""
        all_relations = []
        seen_relations = set()
        
        for chapter in chapters:
            text = chapter.get("content", "")
            relations = self.extract(text, concepts)
            
            for rel in relations:
                rel_key = (rel.source, rel.target, rel.relation_type.value)
                if rel_key not in seen_relations:
                    all_relations.append(rel)
                    seen_relations.add(rel_key)
        
        # 按强度排序
        all_relations.sort(key=lambda x: x.strength, reverse=True)
        
        return all_relations

    def build_relation_graph(self, relations: List[Relation]) -> dict:
        """构建关系图"""
        graph = {
            "nodes": set(),
            "edges": []
        }
        
        for rel in relations:
            graph["nodes"].add(rel.source)
            graph["nodes"].add(rel.target)
            graph["edges"].append({
                "source": rel.source,
                "target": rel.target,
                "type": rel.relation_type.value,
                "strength": rel.strength
            })
        
        graph["nodes"] = list(graph["nodes"])
        
        return graph