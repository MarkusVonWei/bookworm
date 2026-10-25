"""测试限流和书籍数量限制"""

import sys
import time
sys.path.insert(0, '/Users/marvin/workspace/life_project/bookworm')

from src.bookworm.api.rate_limit import RateLimitMiddleware


def test_rate_limit_basic():
    """测试基本限流逻辑"""
    print("=== 测试基本限流 ===")
    
    # 创建一个模拟的限流器
    middleware = RateLimitMiddleware(
        app=None,
        default_limit=5,  # 5次/10秒（用于测试）
        default_window=10,
        upload_limit=2,   # 2次/60秒（用于测试）
        upload_window=60
    )
    
    # 测试普通路径限流
    print("\n测试普通路径限流 (5次/10秒):")
    for i in range(6):
        allowed, limit, window = middleware._check_rate_limit("test_ip", "/api/bookshelf/books")
        status = "✓ 允许" if allowed else "✗ 限流"
        print(f"  请求 {i+1}: {status} (剩余 {limit - len(middleware.requests['test_ip'])} 次)")
        time.sleep(0.1)
    
    # 重置
    middleware.requests.clear()
    
    # 测试重资源路径限流
    print("\n测试重资源路径限流 (2次/60秒):")
    for i in range(3):
        allowed, limit, window = middleware._check_rate_limit("test_ip_2", "/api/bookshelf/recognize")
        status = "✓ 允许" if allowed else "✗ 限流"
        print(f"  请求 {i+1}: {status} (剩余 {limit - len(middleware.requests['test_ip_2'])} 次)")
        time.sleep(0.1)
    
    print("\n=== 测试完成 ===")


def test_book_limit():
    """测试书籍数量限制"""
    print("\n=== 测试书籍数量限制 ===")
    print(f"MAX_BOOKS_PER_USER = 60")
    print("书籍数量限制已配置，实际测试需要数据库连接")


if __name__ == "__main__":
    test_rate_limit_basic()
    test_book_limit()
