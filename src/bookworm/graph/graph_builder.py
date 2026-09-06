from typing import List, Dict, Any, Optional
import logging

from ..parsers.base import ParsedBook
from ..extractors.concept_extractor import ConceptExtractor, Concept
from ..extractors.argument_extractor import ArgumentExtractor, Argument
from ..extractors.relation_extractor import RelationExtractor, Relation
from .neo4j_client import Neo4jClient

logger = logging.getLogger("bookworm")


class GraphBuilder:
    """知识图谱构建器"""

    def __init__(self, neo4j_client: Neo4jClient = None, llm=None):
        self.neo4j_client = neo4j_client or Neo4jClient()
        self.concept_extractor = ConceptExtractor(llm=llm)
        self.argument_extractor = ArgumentExtractor(llm=llm)
        self.relation_extractor = RelationExtractor(llm=llm)

    def build_from_book(self, parsed_book: ParsedBook) -> Dict[str, Any]:
        """从解析后的书籍构建知识图谱"""
        logger.info(f"开始构建知识图谱: {parsed_book.metadata.title}")
        
        # 创建书籍节点
        book_node = self.neo4j_client.create_book(
            title=parsed_book.metadata.title,
            author=parsed_book.metadata.author,
            file_path=parsed_book.metadata.file_path
        )
        
        # 处理每个章节
        all_concepts = []
        all_arguments = []
        all_relations = []
        
        for i, chapter in enumerate(parsed_book.chapters):
            logger.info(f"处理章节 {i+1}/{len(parsed_book.chapters)}: {chapter.title}")
            
            # 创建章节节点
            chapter_node = self.neo4j_client.create_chapter(
                title=chapter.title,
                index=chapter.index,
                book_title=parsed_book.metadata.title
            )
            
            # 提取概念
            logger.info(f"提取章节概念: {chapter.title}")
            concepts = self.concept_extractor.extract(chapter.content)
            all_concepts.extend(concepts)
            
            # 提取观点
            logger.info(f"提取章节观点: {chapter.title}")
            arguments = self.argument_extractor.extract(chapter.content)
            all_arguments.extend(arguments)
        
        # 去重概念
        unique_concepts = self._deduplicate_concepts(all_concepts)
        logger.info(f"概念去重: {len(all_concepts)} -> {len(unique_concepts)}")
        
        # 创建概念节点
        concept_names = []
        for concept in unique_concepts:
            self.neo4j_client.create_concept(
                name=concept.name,
                definition=concept.definition,
                importance=concept.importance,
                context=concept.context
            )
            concept_names.append(concept.name)
        
        # 创建观点节点
        for argument in all_arguments:
            self.neo4j_client.create_argument(
                claim=argument.claim,
                premises=argument.premises,
                conclusion=argument.conclusion,
                strength=argument.strength
            )
        
        # 提取关系
        logger.info("开始提取章节间关系")
        all_relations = self.relation_extractor.extract_from_chapters(
            [{"content": ch.content} for ch in parsed_book.chapters],
            concept_names
        )
        
        # 创建关系
        for relation in all_relations:
            self.neo4j_client.create_relation(
                source_name=relation.source,
                target_name=relation.target,
                relation_type=relation.relation_type.value,
                strength=relation.strength,
                context=relation.context
            )
        
        logger.info(f"知识图谱构建完成: 概念={len(unique_concepts)}, 观点={len(all_arguments)}, 关系={len(all_relations)}")
        
        return {
            "book": book_node,
            "concepts_count": len(unique_concepts),
            "arguments_count": len(all_arguments),
            "relations_count": len(all_relations)
        }

    def _deduplicate_concepts(self, concepts: List[Concept]) -> List[Concept]:
        """去重概念"""
        unique_concepts = []
        seen_names = set()
        
        for concept in concepts:
            if concept.name not in seen_names:
                unique_concepts.append(concept)
                seen_names.add(concept.name)
        
        # 按重要性排序
        unique_concepts.sort(key=lambda x: x.importance, reverse=True)
        
        return unique_concepts

    def build_from_text(self, text: str, book_title: str = "Unknown") -> Dict[str, Any]:
        """从纯文本构建知识图谱"""
        # 创建书籍节点
        book_node = self.neo4j_client.create_book(title=book_title)
        
        # 提取概念
        concepts = self.concept_extractor.extract(text)
        
        # 创建概念节点
        concept_names = []
        for concept in concepts:
            self.neo4j_client.create_concept(
                name=concept.name,
                definition=concept.definition,
                importance=concept.importance,
                context=concept.context
            )
            concept_names.append(concept.name)
        
        # 提取观点
        arguments = self.argument_extractor.extract(text)
        
        # 创建观点节点
        for argument in arguments:
            self.neo4j_client.create_argument(
                claim=argument.claim,
                premises=argument.premises,
                conclusion=argument.conclusion,
                strength=argument.strength
            )
        
        # 提取关系
        relations = self.relation_extractor.extract(text, concept_names)
        
        # 创建关系
        for relation in relations:
            self.neo4j_client.create_relation(
                source_name=relation.source,
                target_name=relation.target,
                relation_type=relation.relation_type.value,
                strength=relation.strength,
                context=relation.context
            )
        
        return {
            "book": book_node,
            "concepts_count": len(concepts),
            "arguments_count": len(arguments),
            "relations_count": len(relations)
        }

    def query_concept(self, concept_name: str) -> Dict[str, Any]:
        """查询概念及其关系"""
        concept = self.neo4j_client.get_concept(concept_name)
        if not concept:
            return {"error": f"概念 '{concept_name}' 不存在"}
        
        related = self.neo4j_client.get_related_concepts(concept_name)
        
        return {
            "concept": concept,
            "related_concepts": related
        }

    def search_concepts(self, keyword: str) -> List[Dict[str, Any]]:
        """搜索概念"""
        return self.neo4j_client.search_concepts(keyword)

    def get_concept_graph(self, concept_name: str, depth: int = 2) -> Dict[str, Any]:
        """获取概念的关系图"""
        return self.neo4j_client.get_concept_graph(concept_name, depth)