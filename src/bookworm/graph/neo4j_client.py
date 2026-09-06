import os
import logging
from typing import List, Dict, Any, Optional
from contextlib import contextmanager

from neo4j import GraphDatabase, Driver, Session

from config.settings import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE

# 配置日志
logger = logging.getLogger("bookworm")


class Neo4jClient:
    """Neo4j数据库客户端"""

    def __init__(self, uri: str = None, username: str = None, password: str = None, database: str = None):
        self.uri = uri or NEO4J_URI
        self.username = username or NEO4J_USERNAME
        self.password = password or NEO4J_PASSWORD
        self.database = database or NEO4J_DATABASE
        self._driver: Optional[Driver] = None
        
        logger.info(f"初始化Neo4j客户端: {self.uri}")

    @property
    def driver(self) -> Driver:
        """获取数据库驱动"""
        if self._driver is None:
            logger.info(f"创建Neo4j驱动: {self.uri}")
            
            # 如果密码为空，使用无密码认证
            if not self.password:
                logger.info("使用无密码认证")
                self._driver = GraphDatabase.driver(self.uri)
            else:
                logger.info("使用用户名密码认证")
                self._driver = GraphDatabase.driver(
                    self.uri,
                    auth=(self.username, self.password)
                )
            
            logger.info("Neo4j驱动创建成功")
        
        return self._driver

    @contextmanager
    def get_session(self):
        """获取数据库会话上下文管理器"""
        session = self.driver.session(database=self.database)
        try:
            yield session
        finally:
            session.close()

    def close(self):
        """关闭数据库连接"""
        if self._driver:
            self._driver.close()
            self._driver = None

    def verify_connectivity(self) -> bool:
        """验证数据库连接"""
        try:
            self.driver.verify_connectivity()
            return True
        except Exception as e:
            print(f"Neo4j连接失败: {e}")
            return False

    def create_indexes(self):
        """创建必要的索引"""
        with self.get_session() as session:
            # 为Concept节点创建索引
            session.run("""
                CREATE INDEX concept_name_index IF NOT EXISTS
                FOR (c:Concept) ON (c.name)
            """)
            
            # 为Argument节点创建索引
            session.run("""
                CREATE INDEX argument_claim_index IF NOT EXISTS
                FOR (a:Argument) ON (a.claim)
            """)
            
            # 为Book节点创建索引
            session.run("""
                CREATE INDEX book_title_index IF NOT EXISTS
                FOR (b:Book) ON (b.title)
            """)

    def clear_database(self):
        """清空数据库（谨慎使用）"""
        with self.get_session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    # 概念相关操作
    def create_concept(self, name: str, definition: str, importance: float = 0.5, context: str = "") -> Dict[str, Any]:
        """创建概念节点"""
        with self.get_session() as session:
            result = session.run("""
                MERGE (c:Concept {name: $name})
                SET c.definition = $definition,
                    c.importance = $importance,
                    c.context = $context,
                    c.created_at = datetime()
                RETURN c
            """, name=name, definition=definition, importance=importance, context=context)
            
            record = result.single()
            return dict(record["c"]) if record else None

    def get_concept(self, name: str) -> Optional[Dict[str, Any]]:
        """获取概念节点"""
        with self.get_session() as session:
            result = session.run("""
                MATCH (c:Concept {name: $name})
                RETURN c
            """, name=name)
            
            record = result.single()
            return dict(record["c"]) if record else None

    def get_all_concepts(self) -> List[Dict[str, Any]]:
        """获取所有概念"""
        with self.get_session() as session:
            result = session.run("""
                MATCH (c:Concept)
                RETURN c
                ORDER BY c.importance DESC
            """)
            
            return [dict(record["c"]) for record in result]

    # 观点相关操作
    def create_argument(self, claim: str, premises: List[str], conclusion: str, strength: float = 0.5) -> Dict[str, Any]:
        """创建观点节点"""
        with self.get_session() as session:
            result = session.run("""
                MERGE (a:Argument {claim: $claim})
                SET a.premises = $premises,
                    a.conclusion = $conclusion,
                    a.strength = $strength,
                    a.created_at = datetime()
                RETURN a
            """, claim=claim, premises=premises, conclusion=conclusion, strength=strength)
            
            record = result.single()
            return dict(record["a"]) if record else None

    def get_argument(self, claim: str) -> Optional[Dict[str, Any]]:
        """获取观点节点"""
        with self.get_session() as session:
            result = session.run("""
                MATCH (a:Argument {claim: $claim})
                RETURN a
            """, claim=claim)
            
            record = result.single()
            return dict(record["a"]) if record else None

    # 书籍相关操作
    def create_book(self, title: str, author: str = None, file_path: str = None) -> Dict[str, Any]:
        """创建书籍节点"""
        with self.get_session() as session:
            result = session.run("""
                MERGE (b:Book {title: $title})
                SET b.author = $author,
                    b.file_path = $file_path,
                    b.created_at = datetime()
                RETURN b
            """, title=title, author=author, file_path=file_path)
            
            record = result.single()
            return dict(record["b"]) if record else None

    # 章节相关操作
    def create_chapter(self, title: str, index: int, book_title: str) -> Dict[str, Any]:
        """创建章节节点"""
        with self.get_session() as session:
            result = session.run("""
                MATCH (b:Book {title: $book_title})
                MERGE (ch:Chapter {title: $title, book: $book_title})
                SET ch.index = $index,
                    ch.created_at = datetime()
                MERGE (b)-[:HAS_CHAPTER]->(ch)
                RETURN ch
            """, title=title, index=index, book_title=book_title)
            
            record = result.single()
            return dict(record["ch"]) if record else None

    # 关系操作
    def create_relation(self, source_name: str, target_name: str, relation_type: str, strength: float = 0.5, context: str = "") -> bool:
        """创建概念间的关系"""
        with self.get_session() as session:
            # 根据关系类型创建不同的关系
            query = f"""
                MATCH (source:Concept {{name: $source_name}})
                MATCH (target:Concept {{name: $target_name}})
                MERGE (source)-[r:{relation_type}]->(target)
                SET r.strength = $strength,
                    r.context = $context,
                    r.created_at = datetime()
                RETURN r
            """
            
            result = session.run(query, source_name=source_name, target_name=target_name, 
                               strength=strength, context=context)
            
            return result.single() is not None

    def get_related_concepts(self, concept_name: str, relation_type: str = None) -> List[Dict[str, Any]]:
        """获取相关概念"""
        with self.get_session() as session:
            if relation_type:
                query = """
                    MATCH (c:Concept {name: $concept_name})-[r]->(related:Concept)
                    WHERE type(r) = $relation_type
                    RETURN related, type(r) as relation_type, r.strength as strength
                """
                result = session.run(query, concept_name=concept_name, relation_type=relation_type)
            else:
                query = """
                    MATCH (c:Concept {name: $concept_name})-[r]->(related:Concept)
                    RETURN related, type(r) as relation_type, r.strength as strength
                """
                result = session.run(query, concept_name=concept_name)
            
            return [
                {
                    "concept": dict(record["related"]),
                    "relation_type": record["relation_type"],
                    "strength": record["strength"]
                }
                for record in result
            ]

    # 查询操作
    def search_concepts(self, keyword: str) -> List[Dict[str, Any]]:
        """搜索概念"""
        with self.get_session() as session:
            result = session.run("""
                MATCH (c:Concept)
                WHERE c.name CONTAINS $keyword OR c.definition CONTAINS $keyword
                RETURN c
                ORDER BY c.importance DESC
            """, keyword=keyword)
            
            return [dict(record["c"]) for record in result]

    def get_concept_graph(self, concept_name: str, depth: int = 2) -> Dict[str, Any]:
        """获取概念的关系图"""
        with self.get_session() as session:
            result = session.run("""
                MATCH path = (c:Concept {name: $concept_name})-[*1..$depth]-(related:Concept)
                RETURN path
            """, concept_name=concept_name, depth=depth)
            
            nodes = set()
            edges = []
            
            for record in result:
                path = record["path"]
                for node in path.nodes:
                    nodes.add(node["name"])
                for rel in path.relationships:
                    edges.append({
                        "source": rel.start_node["name"],
                        "target": rel.end_node["name"],
                        "type": rel.type,
                        "strength": rel.get("strength", 0.5)
                    })
            
            return {
                "nodes": list(nodes),
                "edges": edges
            }