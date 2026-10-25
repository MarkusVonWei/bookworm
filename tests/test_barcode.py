#!/usr/bin/env python3
"""
条形码识别测试脚本

测试条形码识别功能，支持多种图片格式。
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from bookworm.bookshelf.barcode import (
    recognize_barcode_with_crop,
    recognize_barcode,
    validate_isbn13,
    validate_isbn10,
    _extract_isbn,
)


def test_barcode_recognition(image_path: str):
    """测试条形码识别"""
    print(f"\n{'='*60}")
    print(f"测试图片: {image_path}")
    print(f"{'='*60}")

    if not os.path.exists(image_path):
        print(f"❌ 文件不存在: {image_path}")
        return False

    # 识别条形码
    result = recognize_barcode(image_path)

    if result:
        print(f"\n✅ 识别成功!")
        print(f"  条形码类型: {result.get('barcode_type')}")
        print(f"  条形码数据: {result.get('barcode_data')}")

        if 'isbn' in result:
            isbn = result['isbn']
            print(f"  ISBN: {isbn}")

            # 验证 ISBN
            if len(isbn) == 13:
                is_valid = validate_isbn13(isbn)
                print(f"  ISBN-13 有效: {is_valid}")
            elif len(isbn) == 10:
                is_valid = validate_isbn10(isbn)
                print(f"  ISBN-10 有效: {is_valid}")

        if 'rect' in result:
            print(f"  位置: {result['rect']}")

        if 'message' in result:
            print(f"  提示: {result['message']}")

        return True
    else:
        print(f"\n❌ 识别失败")
        return False


def test_isbn_extraction():
    """测试 ISBN 提取逻辑"""
    print(f"\n{'='*60}")
    print("测试 ISBN 提取逻辑")
    print(f"{'='*60}")

    test_cases = [
        # (条形码数据, 条形码类型, 期望的 ISBN)
        ("9787020024759", "EAN13", "9787020024759"),  # 有效的 ISBN-13
        ("9787020024759", "EAN13", "9787020024759"),
        ("7020024759", "EAN10", None),  # ISBN-10 格式
        ("1234567890", "UPCA", None),  # 非 ISBN
        ("9787020024759", "CODE128", "9787020024759"),  # CODE128 格式
    ]

    for data, btype, expected in test_cases:
        result = _extract_isbn(data, btype)
        status = "✅" if result == expected else "❌"
        print(f"  {status} {data} ({btype}) -> {result} (期望: {expected})")


def test_isbn_validation():
    """测试 ISBN 验证"""
    print(f"\n{'='*60}")
    print("测试 ISBN 验证")
    print(f"{'='*60}")

    # ISBN-13 测试
    isbn13_tests = [
        ("9787020024759", True),   # 有效
        ("9787020024750", False),  # 无效校验位
        ("1234567890123", False),  # 无效格式
    ]

    for isbn, expected in isbn13_tests:
        result = validate_isbn13(isbn)
        status = "✅" if result == expected else "❌"
        print(f"  {status} ISBN-13 {isbn}: {result} (期望: {expected})")

    # ISBN-10 测试
    isbn10_tests = [
        ("0131103628", True),   # 有效
        ("0201633612", True),   # 有效
        ("7020024759", False),  # 无效校验位
        ("013110362X", False),  # 无效校验位
    ]

    for isbn, expected in isbn10_tests:
        result = validate_isbn10(isbn)
        status = "✅" if result == expected else "❌"
        print(f"  {status} ISBN-10 {isbn}: {result} (期望: {expected})")


if __name__ == "__main__":
    # 测试 ISBN 提取和验证
    test_isbn_extraction()
    test_isbn_validation()

    # 测试图片识别
    test_images = [
        "/Users/marvin/workspace/life_project/bookworm/imgs/strip_science_history.jpg",
        "/Users/marvin/workspace/life_project/bookworm/imgs/strip_code_test.jpg",
    ]

    for img_path in test_images:
        test_barcode_recognition(img_path)

    print(f"\n{'='*60}")
    print("测试完成")
    print(f"{'='*60}")
