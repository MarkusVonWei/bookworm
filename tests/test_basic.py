#!/usr/bin/env python3
"""
书虫LLM Agent 测试脚本
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.bookworm.parsers.factory import parse_book
from src.bookworm.extractors.concept_extractor import ConceptExtractor
from src.bookworm.extractors.argument_extractor import ArgumentExtractor
from src.bookworm.extractors.relation_extractor import RelationExtractor


def test_parser():
    """测试解析器"""
    print("=== 测试解析器 ===")
    
    # 创建测试文本文件
    test_file = Path("data/books/test_book.txt")
    test_file.parent.mkdir(parents=True, exist_ok=True)
    
    test_content = """
第一章 人工智能概述

人工智能（Artificial Intelligence，AI）是计算机科学的一个分支，旨在创建能够模拟人类智能的系统。

1.1 什么是人工智能

人工智能是指由人制造出来的机器所表现出来的智能。通常人工智能是指通过普通计算机程序来呈现人类智能的技术。

1.2 人工智能的发展历史

人工智能的发展可以追溯到20世纪50年代。1956年，在达特茅斯会议上，人工智能正式被确立为一个学科。

第二章 机器学习基础

机器学习是人工智能的一个重要分支，它使计算机能够从数据中学习，而无需显式编程。

2.1 监督学习

监督学习是机器学习的一种方法，其中模型从标记的训练数据中学习。

2.2 无监督学习

无监督学习是另一种机器学习方法，模型从未标记的数据中发现模式。
"""
    
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(test_content)
    
    # 测试解析
    try:
        parsed_book = parse_book(str(test_file))
        print(f"书籍标题: {parsed_book.metadata.title}")
        print(f"章节数量: {len(parsed_book.chapters)}")
        print(f"总页数: {parsed_book.total_pages}")
        
        for chapter in parsed_book.chapters:
            print(f"  章节 {chapter.index}: {chapter.title}")
        
        print("解析器测试通过！\n")
        return parsed_book
    except Exception as e:
        print(f"解析器测试失败: {e}")
        return None


def test_extractors(parsed_book):
    """测试提取器"""
    print("=== 测试提取器 ===")
    
    if not parsed_book:
        print("没有解析的书籍，跳过测试")
        return
    
    # 测试概念提取（只测试初始化，不实际调用API）
    print("测试概念提取器初始化...")
    try:
        concept_extractor = ConceptExtractor()
        print("概念提取器初始化成功！")
    except Exception as e:
        print(f"概念提取器初始化失败: {e}")
    
    print("提取器测试完成！\n")


def main():
    """主测试函数"""
    print("开始测试书虫LLM Agent...\n")
    
    # 测试解析器
    parsed_book = test_parser()
    
    # 测试提取器
    test_extractors(parsed_book)
    
    print("所有测试完成！")


if __name__ == "__main__":
    main()