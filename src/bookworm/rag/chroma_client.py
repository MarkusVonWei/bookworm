import os
from typing import List, Dict, Any, Optional

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from config.settings import CHROMA_HOST, CHROMA_PORT, CHROMA_COLLECTION


class ChromaClient:
    """ChromaDB向量数据库客户端"""

    def __init__(self, host: str = None, port: int = None, collection_name: str = None):
        self.host = host or CHROMA_HOST
        self.port = port or CHROMA_PORT
        self.collection_name = collection_name or CHROMA_COLLECTION
        self._client = None
        self._collection = None

    @property
    def client(self) -> chromadb.ClientAPI:
        """获取ChromaDB客户端"""
        if self._client is None:
            # 使用本地持久化存储
            self._client = chromadb.PersistentClient(path="./data/chroma_db")
        return self._client

    @property
    def collection(self):
        """获取集合"""
        if self._collection is None:
            # 使用默认的嵌入函数
            embedding_func = embedding_functions.DefaultEmbeddingFunction()
            self._collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=embedding_func,
                metadata={"hnsw:space": "cosine"}
            )
        return self._collection

    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]] = None, ids: List[str] = None):
        """添加文档到向量数据库"""
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(documents))]
        
        if metadatas is None:
            metadatas = [{} for _ in range(len(documents))]
        
        # 分批处理，避免单次请求过大
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i+batch_size]
            batch_metas = metadatas[i:i+batch_size]
            batch_ids = ids[i:i+batch_size]
            
            self.collection.add(
                documents=batch_docs,
                metadatas=batch_metas,
                ids=batch_ids
            )

    def query(self, query_text: str, n_results: int = 5, where: Dict[str, Any] = None) -> Dict[str, Any]:
        """查询相似文档"""
        query_params = {
            "query_texts": [query_text],
            "n_results": n_results
        }
        
        if where:
            query_params["where"] = where
        
        results = self.collection.query(**query_params)
        
        return {
            "documents": results["documents"][0] if results["documents"] else [],
            "metadatas": results["metadatas"][0] if results["metadatas"] else [],
            "distances": results["distances"][0] if results["distances"] else [],
            "ids": results["ids"][0] if results["ids"] else []
        }

    def delete_collection(self):
        """删除集合"""
        self.client.delete_collection(self.collection_name)
        self._collection = None

    def get_collection_stats(self) -> Dict[str, Any]:
        """获取集合统计信息"""
        return {
            "name": self.collection_name,
            "count": self.collection.count()
        }

    def add_chapter_chunks(self, chapter_title: str, chunks: List[str], book_title: str):
        """添加章节分块"""
        documents = []
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            doc_id = f"{book_title}_{chapter_title}_chunk_{i}"
            documents.append(chunk)
            metadatas.append({
                "book_title": book_title,
                "chapter_title": chapter_title,
                "chunk_index": i,
                "source": "chapter"
            })
            ids.append(doc_id)
        
        self.add_documents(documents, metadatas, ids)

    def search_by_metadata(self, where: Dict[str, Any], n_results: int = 10) -> Dict[str, Any]:
        """根据元数据搜索"""
        results = self.collection.get(
            where=where,
            limit=n_results
        )
        
        return {
            "documents": results["documents"] if results["documents"] else [],
            "metadatas": results["metadatas"] if results["metadatas"] else [],
            "ids": results["ids"] if results["ids"] else []
        }