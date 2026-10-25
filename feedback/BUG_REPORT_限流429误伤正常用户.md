# Bug 报告：限流中间件误伤正常用户（上传图片返回 429）

- **日期**：2026-10-25
- **环境**：生产环境（服务器 `book`，`/home/ubuntu/workspace/bookworm`，端口 8000，nginx 反代 `bookworm.icu`）
- **影响接口**：`POST /api/bookshelf/recognize`、`POST /api/bookshelf/books` 等写接口
- **问题文件**：`src/bookworm/api/rate_limit.py`
- **严重程度**：中（正常使用被误拦，用户无法上传图片/识别书籍）
- **修复文件**：见同目录 `rate_limit.py`（已部署到生产并验证）

---

## 1. 现象

用户正常使用小程序上传图片（识别书籍）时，收到 **429 Too Many Requests**：

```json
{"detail": "请求过于频繁，请稍后再试"}
```

但用户当时**并没有高频操作**，只是正常浏览页面后上传了一张图片。

## 2. 排查过程（定位是 nginx 还是后端）

| 检查项 | 结果 | 结论 |
|---|---|---|
| nginx 配置 `bookshelf.conf` | 无 `limit_req` / `limit_conn` 配置 | nginx 不拦截 |
| nginx `error.log` | 无 limit 相关记录 | nginx 不拦截 |
| 后端 `all.log` | 应用自身打出 `POST /api/bookshelf/recognize → 429` | **后端拦截** |
| 响应体 50 字节 | 与 `rate_limit.py` 的 429 文案一致 | 后端拦截 |

**结论：429 由后端 `RateLimitMiddleware` 返回，与 nginx 无关。**

## 3. 根因分析

### 3.1 限流策略（设计意图）

`src/bookworm/api/app.py` 中的挂载配置：

```python
app.add_middleware(
    RateLimitMiddleware,
    default_limit=100,   # 普通请求：10秒100次
    default_window=10,
    upload_limit=10,     # 识别/添加书籍（写操作）：60秒10次
    upload_window=60,
    trusted_proxies=["127.0.0.1", "::1"]
)
```

设计意图：`/api/bookshelf/recognize`、`/api/bookshelf/books` 的**写操作**限制 60 秒 10 次（合理，recognize 调用 MiMo VL 模型有真实成本）。

### 3.2 Bug：计数未按类别区分

`_check_rate_limit()` 中判断是否超额时：

```python
# 判断使用哪个限制策略（阈值选择正确）
is_write = method in ("POST", "PUT", "DELETE", "PATCH")
is_heavy = is_write and any(path.startswith(prefix) for prefix in self.heavy_write_paths)
limit = self.upload_limit if is_heavy else self.default_limit

# ❌ 但计数时统计的是该 IP 的【所有请求】，包括 GET 浏览请求
current_count = len(self.requests.get(ip, []))
if current_count >= limit:
    return False, limit, window
```

**所有请求（GET + POST）都写入同一个 `self.requests[ip]` 列表**，而严格阈值（10 次/60 秒）却用这个总列表计数。于是：

> 用户浏览页面产生的 ~10 个 GET 请求，会把"60 秒 10 次"的**上传额度全部吃掉**，随后一次正常上传即被 429。

### 3.3 附带问题：清理窗口导致计数不一致

`_clean_old_requests(ip, window)` 按**当前请求的窗口**清理记录：
GET 请求窗口是 10 秒，会把 10 秒前的记录删掉，导致写操作 60 秒窗口的计数被中途的 GET 清空，限流实际时紧时松、行为不可预测。

### 3.4 现场证据（与日志完全吻合）

```
19:44:27 ~ 19:44:35   GET /api/user/me              200
19:44:28 ~ 19:44:35   GET /api/bookshelf/books  ×4  200
19:44:29              GET /api/bookshelf/statistics  200
19:44:29              GET /api/bookshelf/statistics  200
19:44:33              GET /api/bookshelf/timeline    200
19:44:55              POST /api/bookshelf/recognize  429  ← 仅 1 次上传即被拦
```

9 个 GET 浏览 + 1 次上传 → 429。用户实际写操作只有 1 次。

## 4. 修复方案

修改 `src/bookworm/api/rate_limit.py`（完整文件见同目录 `rate_limit.py`），核心改动 2 处：

### 4.1 请求记录增加类型标记，计数按类别分开

```python
# 请求记录 {ip: [(timestamp, is_heavy), ...]}   # 原来是 (timestamp, path)

def _count_requests(self, ip: str, is_heavy: bool) -> int:
    """统计当前窗口内该 IP 的请求数（写操作与普通请求分开计数）"""
    now = time.time()
    records = self.requests.get(ip, [])
    if is_heavy:
        return sum(1 for t, h in records if h and now - t < self.upload_window)
    return sum(1 for t, h in records if now - t < self.default_window)
```

### 4.2 清理记录统一按最长窗口（60 秒）保留历史

```python
def _clean_old_requests(self, ip: str):
    cutoff = time.time() - max(self.default_window, self.upload_window)  # 原来按当前请求窗口清理
    ...
```

**保持不变**：限流阈值（100 次/10 秒、写操作 10 次/60 秒）、trusted_proxies、429 响应格式、响应头。

## 5. 验证结果（生产环境实测）

| 场景 | 修复前 | 修复后 |
|---|---|---|
| 刷 15 个 GET 后发起 1 次上传 | ❌ 429 | ✅ 正常到达接口 |
| 60 秒内第 11 次写操作 | 429 | 429（保护依然生效）|
| 超额响应头 | `Retry-After: 60` | 不变 |

## 6. 给负责人的建议（未改动，供参考）

1. **超额语义**：当前"写操作 10 次/60 秒"对批量导入场景可能偏紧，建议改为环境变量可配（如 `RATE_LIMIT_UPLOAD=10`）。
2. **多 worker 扩展**：限流状态在进程内存中，未来若用多 worker/多实例部署，状态不共享，需换 Redis 等共享存储。
3. **`X-RateLimit-Remaining` 头**：仍用总记录数估算，如需精确值可改为传入 `is_heavy` 后用 `_count_requests()` 计算。
4. **日志建议**：429 时记录被拦的 path 与 IP，便于以后排查（当前 429 不落日志，只能从访问日志推断）。

## 7. 部署状态

- 已部署至生产 `/home/ubuntu/workspace/bookworm/src/bookworm/api/rate_limit.py`
- 服务已重启（`APP_DEBUG=false`，单进程 uvicorn）
- 期间未改变任何接口行为与响应格式，仅修正计数逻辑
