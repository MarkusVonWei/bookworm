import logging
from functools import lru_cache

from llama_index.llms.openai import OpenAI

from config.settings import OPENAI_API_KEY, OPENAI_BASE_URL, LLM_MODEL

logger = logging.getLogger("bookworm")


@lru_cache(maxsize=1)
def get_llm_client():
    """获取LLM客户端（单例模式）"""
    logger.info(f"初始化LLM客户端: model={LLM_MODEL}, api_base={OPENAI_BASE_URL}")
    return OpenAI(
        model=LLM_MODEL,
        temperature=0,
        api_key=OPENAI_API_KEY,
        api_base=OPENAI_BASE_URL
    )
