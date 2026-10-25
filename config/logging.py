import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

def setup_logging():
    """配置日志，支持每日轮转，保留6个月"""
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 配置日志格式
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(log_format, datefmt=date_format)
    
    # 创建 handlers
    handlers = []
    
    # 1. 控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)
    
    # 2. 主日志文件 - 每天轮转，保留6个月
    main_handler = TimedRotatingFileHandler(
        filename="logs/app.log",
        when="midnight",
        interval=1,
        backupCount=180,  # 保留6个月 (180天)
        encoding="utf-8"
    )
    main_handler.setFormatter(formatter)
    handlers.append(main_handler)
    
    # 3. 识别日志文件 - 每天轮转，保留6个月
    recognition_handler = TimedRotatingFileHandler(
        filename="logs/recognition.log",
        when="midnight",
        interval=1,
        backupCount=180,  # 保留6个月
        encoding="utf-8"
    )
    recognition_handler.setFormatter(formatter)
    recognition_handler.addFilter(lambda record: 'recognition' in record.name)
    handlers.append(recognition_handler)
    
    # 配置根日志记录器
    logging.basicConfig(
        level=logging.DEBUG,
        format=log_format,
        datefmt=date_format,
        handlers=handlers
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
    logger.info(f"日志配置: 每日轮转，保留6个月")

# 创建全局日志记录器
logger = setup_logging()
log_config(logger)
