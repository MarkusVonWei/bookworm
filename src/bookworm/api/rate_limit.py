"""限流中间件"""

import time
from typing import Optional
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    简单的内存限流中间件

    策略：滑动窗口限流
    - 每个 IP 在 10 秒内最多 100 次请求
    - 对于识别/添加书籍等写操作，限制更严格（60秒10次）
    - 只对写操作 (POST/PUT/DELETE/PATCH) 应用严格限制，GET 请求使用默认限制
    """

    def __init__(self, app,
                 default_limit: int = 100,
                 default_window: int = 10,
                 upload_limit: int = 10,
                 upload_window: int = 60,
                 trusted_proxies: Optional[list] = None):
        super().__init__(app)
        self.default_limit = default_limit  # 默认限制：10秒100次
        self.default_window = default_window
        self.upload_limit = upload_limit    # 上传/识别限制：60秒10次
        self.upload_window = upload_window

        # 信任的代理 IP 列表（只信任这些代理转发的 X-Forwarded-For）
        self.trusted_proxies = set(trusted_proxies or [])

        # 请求记录 {ip: [(timestamp, path), ...]}
        self.requests = {}

        # 需要更严格限制的路径前缀（只对写操作生效）
        self.heavy_write_paths = ["/api/bookshelf/recognize", "/api/bookshelf/books"]

        # 定期清理过期 IP 记录的计数器
        self._cleanup_counter = 0
        self._cleanup_interval = 100  # 每 100 个请求清理一次

    def _get_client_ip(self, request: Request) -> str:
        """获取客户端 IP，只信任来自受信任代理的 X-Forwarded-For"""
        client_ip = request.client.host if request.client else "unknown"

        # 只有当请求来自受信任代理时，才解析 X-Forwarded-For
        if client_ip in self.trusted_proxies:
            forwarded = request.headers.get("X-Forwarded-For")
            if forwarded:
                # 取第一个 IP（最接近客户端的）
                client_ip = forwarded.split(",")[0].strip()

        return client_ip

    def _clean_old_requests(self, ip: str, window: int):
        """清理过期的请求记录"""
        cutoff = time.time() - window
        if ip in self.requests:
            self.requests[ip] = [(t, p) for t, p in self.requests[ip] if t > cutoff]

            # 如果该 IP 的记录为空，删除该 key 以释放内存
            if not self.requests[ip]:
                del self.requests[ip]

    def _cleanup_stale_ips(self):
        """定期清理所有过期的 IP 记录（防止内存泄漏）"""
        self._cleanup_counter += 1
        if self._cleanup_counter < self._cleanup_interval:
            return

        self._cleanup_counter = 0
        now = time.time()
        max_window = max(self.default_window, self.upload_window)
        cutoff = now - max_window

        # 清理所有过期记录
        empty_ips = []
        for ip, records in self.requests.items():
            self.requests[ip] = [(t, p) for t, p in records if t > cutoff]
            if not self.requests[ip]:
                empty_ips.append(ip)

        # 删除空 IP 记录
        for ip in empty_ips:
            del self.requests[ip]

    def _check_rate_limit(self, ip: str, path: str, method: str) -> tuple[bool, int, int]:
        """
        检查是否超过限流
        返回: (是否允许, 限制次数, 窗口秒数)
        """
        # 判断使用哪个限制策略
        # 只对写操作 (POST/PUT/DELETE/PATCH) 应用严格限制
        is_write = method in ("POST", "PUT", "DELETE", "PATCH")
        is_heavy = is_write and any(path.startswith(prefix) for prefix in self.heavy_write_paths)

        limit = self.upload_limit if is_heavy else self.default_limit
        window = self.upload_window if is_heavy else self.default_window

        # 清理过期记录
        self._clean_old_requests(ip, window)

        # 定期清理所有过期 IP
        self._cleanup_stale_ips()

        # 检查当前窗口内的请求数
        current_count = len(self.requests.get(ip, []))

        if current_count >= limit:
            return False, limit, window

        # 记录本次请求
        if ip not in self.requests:
            self.requests[ip] = []
        self.requests[ip].append((time.time(), path))
        return True, limit, window

    async def dispatch(self, request: Request, call_next):
        # 获取客户端 IP（只信任受信任代理的 X-Forwarded-For）
        client_ip = self._get_client_ip(request)

        path = request.url.path
        method = request.method

        # 检查限流
        allowed, limit, window = self._check_rate_limit(client_ip, path, method)

        if not allowed:
            return Response(
                content='{"detail": "请求过于频繁，请稍后再试"}',
                status_code=429,
                media_type="application/json",
                headers={
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Window": str(window),
                    "Retry-After": str(window)
                }
            )

        # 记录响应时间
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        # 添加限流信息到响应头
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(max(0, limit - len(self.requests.get(client_ip, []))))
        response.headers["X-Process-Time"] = f"{process_time:.3f}"

        return response