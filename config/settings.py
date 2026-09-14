import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(override=True)

# 项目根目录
BASE_DIR = Path(__file__).parent.parent

# OpenAI配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://token-plan-cn.xiaomimimo.com/v1")

# MiMo VL配置（用于书籍识别）
MIMO_API_KEY = os.getenv("MIMO_API_KEY", OPENAI_API_KEY)
MIMO_API_BASE = os.getenv("MIMO_API_BASE", OPENAI_BASE_URL)

# Anthropic配置
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Neo4j配置
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

# ChromaDB配置
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "bookworm")

# 应用配置
APP_ENV = os.getenv("APP_ENV", "development")
APP_DEBUG = os.getenv("APP_DEBUG", "false").lower() == "true"
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8000"))

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")

# 数据目录配置
DATA_DIR = BASE_DIR / os.getenv("DATA_DIR", "data")
BOOKS_DIR = BASE_DIR / os.getenv("BOOKS_DIR", "data/books")
KNOWLEDGE_DIR = BASE_DIR / os.getenv("KNOWLEDGE_DIR", "data/knowledge")
CACHE_DIR = BASE_DIR / os.getenv("CACHE_DIR", "data/cache")
UPLOAD_DIR = BASE_DIR / os.getenv("UPLOAD_DIR", "data/uploads")

# 确保目录存在
for dir_path in [DATA_DIR, BOOKS_DIR, KNOWLEDGE_DIR, CACHE_DIR, UPLOAD_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# LlamaIndex配置
LLM_MODEL = os.getenv("LLM_MODEL", "mimo-v2.5")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")

# 文档处理配置
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1024"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "20"))