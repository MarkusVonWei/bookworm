"""书虫LLM Agent - 主应用"""

import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# 导入书架模块
from ..bookshelf.api import router as bookshelf_router
from ..bookshelf.migrate import migrate_db
from ..database import init_db, SessionLocal
from .rate_limit import RateLimitMiddleware

# 配置日志
logger = logging.getLogger("bookworm")


# 创建FastAPI应用
def create_app() -> FastAPI:
    app = FastAPI(
        title="我的书架",
        description="个人阅读管理 - 数字书架",
        version="1.0.0"
    )
    
    # 添加限流中间件 (必须在CORS之前添加)
    app.add_middleware(
        RateLimitMiddleware,
        default_limit=100,   # 默认：10秒100次请求
        default_window=10,
        upload_limit=10,     # 识别/添加书籍：60秒10次
        upload_window=60,
        trusted_proxies=["127.0.0.1", "::1"]  # 信任 Nginx 代理
    )
    
    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 初始化数据库
    init_db()

    # 执行数据库迁移 (添加 user_id 字段等)
    db = SessionLocal()
    try:
        migrate_db(db)
    finally:
        db.close()
    
    # 注册路由
    app.include_router(bookshelf_router)
    
    # 静态文件服务（用于上传的图片）
    upload_dir = Path("data/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/data", StaticFiles(directory="data"), name="data")
    
    @app.get("/")
    async def root():
        return {"message": "欢迎使用我的书架"}
    
    @app.get("/health")
    async def health_check():
        """健康检查"""
        return {"status": "healthy"}
    
    return app


# 创建应用实例
app = create_app()
