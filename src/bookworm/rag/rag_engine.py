import logging
from typing import List, Dict, Any, Optional

from ..utils import get_llm_client
from .chroma_client import ChromaClient
from ..graph.neo4j_client import Neo4jClient

logger = logging.getLogger("bookworm")


class RAGEngine:
    """检索增强生成引擎"""

    def __init__(self, chroma_client: ChromaClient = None, neo4j_client: Neo4jClient = None, llm=None):
        self.chroma_client = chroma_client or ChromaClient()
        self.neo4j_client = neo4j_client or Neo4jClient()
        self.llm = llm or get_llm_client()
        
        self.qa_prompt = """
        你是一个专业的书籍分析助手。请根据以下上下文信息回答用户的问题。

        要求：
        1. 基于提供的上下文信息回答问题
        2. 如果上下文中没有相关信息，请明确说明
        3. 引用相关的来源信息
        4. 保持回答准确、简洁

        上下文信息：
        {context}

        知识图谱信息：
        {graph_info}

        用户问题：{question}

        请提供详细的回答：
        """

    def answer_question(self, question: str, book_title: str = None) -> Dict[str, Any]:
        """回答用户问题"""
        logger.info(f"收到问题: {question[:100]}..., book_title={book_title}")
        
        # 1. 从向量数据库检索相关文档
        context_docs = self._retrieve_from_vector_db(question, book_title)
        logger.info(f"向量检索返回 {len(context_docs)} 条结果")
        
        # 2. 从知识图谱检索相关信息
        graph_info = self._retrieve_from_graph(question)
        logger.info(f"图谱检索返回 {len(graph_info.get('concepts', []))} 个概念, {len(graph_info.get('relations', []))} 条关系")
        
        # 3. 组装上下文
        context = self._assemble_context(context_docs, graph_info)
        
        # 4. 生成答案
        answer = self._generate_answer(question, context, graph_info)
        logger.info(f"答案生成完成, 长度: {len(answer)}")
        
        return {
            "answer": answer,
            "sources": context_docs,
            "graph_info": graph_info
        }

    def _retrieve_from_vector_db(self, question: str, book_title: str = None) -> List[Dict[str, Any]]:
        """从向量数据库检索相关文档"""
        where = {}
        if book_title:
            where["book_title"] = book_title
        
        results = self.chroma_client.query(
            query_text=question,
            n_results=5,
            where=where if where else None
        )
        
        documents = []
        for i in range(len(results["documents"])):
            documents.append({
                "content": results["documents"][i],
                "metadata": results["metadatas"][i] if results["metadatas"] else {},
                "distance": results["distances"][i] if results["distances"] else 0
            })
        
        return documents

    def _retrieve_from_graph(self, question: str) -> Dict[str, Any]:
        """从知识图谱检索相关信息"""
        # 从问题中提取关键词
        keywords = self._extract_keywords(question)
        
        graph_info = {
            "concepts": [],
            "relations": []
        }
        
        for keyword in keywords:
            # 搜索相关概念
            concepts = self.neo4j_client.search_concepts(keyword)
            if concepts:
                graph_info["concepts"].extend(concepts[:3])  # 每个关键词最多3个概念
            
            # 获取概念的关系
            for concept in concepts[:2]:  # 只处理前2个概念
                related = self.neo4j_client.get_related_concepts(concept["name"])
                if related:
                    graph_info["relations"].extend(related[:2])
        
        return graph_info

    def _extract_keywords(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        # 简单的关键词提取：按空格分词，去除停用词
        stop_words = {"的", "了", "是", "在", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这"}
        
        words = text.split()
        keywords = [word for word in words if word not in stop_words and len(word) > 1]
        
        return keywords[:5]  # 最多返回5个关键词

    def _assemble_context(self, context_docs: List[Dict[str, Any]], graph_info: Dict[str, Any]) -> str:
        """组装上下文"""
        context_parts = []
        
        # 添加文档上下文
        for i, doc in enumerate(context_docs[:3]):  # 最多3个文档
            context_parts.append(f"文档片段 {i+1}:\n{doc['content']}")
        
        # 添加图谱信息
        if graph_info.get("concepts"):
            context_parts.append("\n相关概念:")
            for concept in graph_info["concepts"][:3]:
                context_parts.append(f"- {concept['name']}: {concept.get('definition', '无定义')}")
        
        if graph_info.get("relations"):
            context_parts.append("\n概念关系:")
            for rel in graph_info["relations"][:3]:
                context_parts.append(f"- {rel.get('source', '')} -> {rel.get('target', '')} ({rel.get('relation_type', '')})")
        
        return "\n\n".join(context_parts)

    def _generate_answer(self, question: str, context: str, graph_info: Dict[str, Any]) -> str:
        """生成答案"""
        graph_info_str = ""
        if graph_info.get("concepts"):
            graph_info_str = "概念: " + ", ".join([c["name"] for c in graph_info["concepts"][:5]])
        
        prompt = self.qa_prompt.format(
            context=context,
            graph_info=graph_info_str,
            question=question
        )
        
        try:
            logger.debug("开始调用LLM生成答案")
            response = self.llm.complete(prompt)
            return response.text
        except Exception as e:
            logger.error(f"LLM生成答案失败: {e}", exc_info=True)
            return f"生成答案时出错: {str(e)}"

    def add_book_to_index(self, parsed_book):
        """将书籍添加到向量索引"""
        logger.info(f"开始添加书籍到向量索引: {parsed_book.metadata.title}")
        for i, chapter in enumerate(parsed_book.chapters):
            # 将章节内容分块
            chunks = self._split_text_into_chunks(chapter.content)
            logger.info(f"章节 '{chapter.title}' 分为 {len(chunks)} 个块")
            
            # 添加到ChromaDB
            self.chroma_client.add_chapter_chunks(
                chapter_title=chapter.title,
                chunks=chunks,
                book_title=parsed_book.metadata.title
            )
        logger.info(f"书籍添加到向量索引完成: {parsed_book.metadata.title}")

    def _split_text_into_chunks(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """将文本分块"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # 如果不是最后一块，尝试在句号处断开
            if end < len(text):
                # 寻找最近的句号
                last_period = text.rfind('。', start, end)
                if last_period == -1:
                    last_period = text.rfind('.', start, end)
                if last_period != -1:
                    end = last_period + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
        
        return chunks