import logging
import sys
from pathlib import Path

def setup_logging():
    """配置日志"""
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 配置日志格式
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # 配置根日志记录器
    logging.basicConfig(
        level=logging.DEBUG,
        format=log_format,
        datefmt=date_format,
        handlers=[
            # 输出到文件
            logging.FileHandler(
                "logs/app.log",
                encoding="utf-8"
            ),
            # 输出到控制台
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # 创建应用日志记录器
    logger = logging.getLogger("bookworm")
    logger.setLevel(logging.DEBUG)
    
    return logger

def log_config(logger):
    """记录关键配置信息"""
    from config.settings import OPENAI_API_KEY, OPENAI_BASE_URL, NEO4J_URI, LLM_MODEL
    masked_key = (OPENAI_API_KEY[:8] + "..." + OPENAI_API_KEY[-4:]) if OPENAI_API_KEY and len(OPENAI_API_KEY) > 12 else "未设置"
    logger.info(f"OpenAI配置: model={LLM_MODEL}, api_base={OPENAI_BASE_URL}, api_key={masked_key}")
    logger.info(f"Neo4j配置: uri={NEO4J_URI}")

# 创建全局日志记录器
logger = setup_logging()
log_config(logger)