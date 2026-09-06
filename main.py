import uvicorn
from config.settings import APP_HOST, APP_PORT, APP_DEBUG
from config.logging import logger


def main():
    """主函数"""
    logger.info("启动书虫LLM Agent服务")
    logger.info(f"服务地址: {APP_HOST}:{APP_PORT}")
    logger.info(f"调试模式: {APP_DEBUG}")
    
    uvicorn.run(
        "src.bookworm.api.app:app",
        host=APP_HOST,
        port=APP_PORT,
        reload=APP_DEBUG
    )


if __name__ == "__main__":
    main()