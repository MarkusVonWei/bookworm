# 限流和书籍数量限制功能说明

## 1. 书籍数量限制

### 配置
- **限制**: 每个用户最多 60 本书
- **位置**: `src/bookworm/bookshelf/service.py`
- **常量**: `MAX_BOOKS_PER_USER = 60`

### 实现逻辑
```python
def add_book(self, book_data: Dict[str, Any]) -> Book:
    # 检查用户书籍数量限制
    current_count = self.db.query(func.count(Book.id))\
        .filter(Book.user_id == user_id)\
        .scalar()
    
    if current_count >= MAX_BOOKS_PER_USER:
        raise ValueError(f"每个用户最多只能上传 {MAX_BOOKS_PER_USER} 本书，已达上限")
    # ... 继续添加书籍
```

### 错误响应
- **HTTP 状态码**: 403 Forbidden
- **错误信息**: `{"detail": "每个用户最多只能上传 60 本书，已达上限"}`

---

## 2. API 限流

### 策略配置
| 路径类型 | 限制 | 窗口 | 说明 |
|----------|------|------|------|
| 普通 API | 100 次 | 10 秒 | 查询、搜索等轻量操作 |
| 重资源 API | 10 次 | 60 秒 | 识别、添加书籍等重操作 |

### 重资源路径
- `/api/bookshelf/recognize` - 书籍识别
- `/api/bookshelf/books` - 添加书籍（POST）

### 实现
- **中间件**: `src/bookworm/api/rate_limit.py`
- **限流策略**: 滑动窗口（基于 IP 地址）
- **存储方式**: 内存存储（重启后重置）

### 响应头
每个响应都会包含以下限流信息：
```
X-RateLimit-Limit: 100          # 当前窗口的限制次数
X-RateLimit-Remaining: 95       # 剩余可用次数
X-RateLimit-Window: 10          # 窗口大小（秒）
X-Process-Time: 0.023           # 处理时间（秒）
```

### 错误响应
当超过限流时：
- **HTTP 状态码**: 429 Too Many Requests
- **错误信息**: `{"detail": "请求过于频繁，请稍后再试"}`
- **响应头**: `Retry-After: 10`（建议等待时间）

---

## 3. 测试

### 运行测试
```bash
cd /Users/marvin/workspace/life_project/bookworm
source venv/bin/activate
python3 tests/test_rate_limit.py
```

### 测试输出示例
```
=== 测试基本限流 ===
测试普通路径限流 (5次/10秒):
  请求 1: ✓ 允许 (剩余 1 次)
  请求 2: ✓ 允许 (剩余 0 次)
  请求 3: ✗ 限流 (剩余 0 次)

测试重资源路径限流 (2次/60秒):
  请求 1: ✓ 允许 (剩余 1 次)
  请求 2: ✓ 允许 (剩余 0 次)
  请求 3: ✗ 限流 (剩余 0 次)

=== 测试书籍数量限制 ===
MAX_BOOKS_PER_USER = 60
```

---

## 4. 调整配置

### 修改书籍数量限制
编辑 `src/bookworm/bookshelf/service.py`:
```python
MAX_BOOKS_PER_USER = 60  # 修改此值
```

### 修改限流策略
编辑 `src/bookworm/api/app.py`:
```python
app.add_middleware(
    RateLimitMiddleware,
    default_limit=100,   # 普通API限制
    default_window=10,   # 普通API窗口（秒）
    upload_limit=10,     # 重资源API限制
    upload_window=60     # 重资源API窗口（秒）
)
```

---

## 5. 注意事项

1. **限流存储**: 当前使用内存存储，服务重启后限流状态会重置
2. **分布式部署**: 如果部署多个实例，需要使用 Redis 等外部存储来共享限流状态
3. **IP 伪造**: 当前通过 `X-Forwarded-For` 获取真实 IP，需确保反向代理配置正确
4. **书籍删除**: 删除书籍不会释放配额，只有实际删除后才能添加新书
