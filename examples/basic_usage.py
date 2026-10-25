#!/usr/bin/env python3
"""
书虫LLM Agent 使用示例
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.bookworm.parsers.factory import parse_book
from src.bookworm.graph.graph_builder import GraphBuilder
from src.bookworm.rag.rag_engine import RAGEngine


def example_usage():
    """示例用法"""
    print("=== 书虫LLM Agent 使用示例 ===\n")
    
    # 1. 解析书籍
    print("1. 解析书籍")
    book_path = "data/books/example.txt"
    
    # 创建示例书籍
    create_example_book(book_path)
    
    # 解析书籍
    parsed_book = parse_book(book_path)
    print(f"   书籍标题: {parsed_book.metadata.title}")
    print(f"   章节数量: {len(parsed_book.chapters)}")
    print()
    
    # 2. 构建知识图谱
    print("2. 构建知识图谱")
    graph_builder = GraphBuilder()
    result = graph_builder.build_from_book(parsed_book)
    print(f"   概念数量: {result['concepts_count']}")
    print(f"   观点数量: {result['arguments_count']}")
    print(f"   关系数量: {result['relations_count']}")
    print()
    
    # 3. 提问问题
    print("3. 提问问题")
    rag_engine = RAGEngine()
    rag_engine.add_book_to_index(parsed_book)
    
    question = "这本书的主要观点是什么？"
    print(f"   问题: {question}")
    
    answer = rag_engine.answer_question(question)
    print(f"   答案: {answer['answer'][:200]}...")
    print()
    
    print("=== 示例完成 ===")


def create_example_book(file_path: str):
    """创建示例书籍"""
    content = """
第一章 人工智能概述

人工智能（Artificial Intelligence，AI）是计算机科学的一个分支，旨在创建能够模拟人类智能的系统。

1.1 什么是人工智能

人工智能是指由人制造出来的机器所表现出来的智能。通常人工智能是指通过普通计算机程序来呈现人类智能的技术。

人工智能的研究包括机器人、语言识别、图像识别、自然语言处理和专家系统等。

1.2 人工智能的发展历史

人工智能的发展可以追溯到20世纪50年代。1956年，在达特茅斯会议上，人工智能正式被确立为一个学科。

第二章 机器学习基础

机器学习是人工智能的一个重要分支，它使计算机能够从数据中学习，而无需显式编程。

2.1 监督学习

监督学习是机器学习的一种方法，其中模型从标记的训练数据中学习。常见的监督学习算法包括线性回归、逻辑回归、支持向量机等。

2.2 无监督学习

无监督学习是另一种机器学习方法，模型从未标记的数据中发现模式。聚类分析和降维是无监督学习的典型应用。
"""
    
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    example_usage()