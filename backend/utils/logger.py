import logging
import sys
from backend.core.config import settings


class ColorFormatter(logging.Formatter):
    """彩色日志格式化器"""

    COLORS = {
        logging.DEBUG: "\x1b[38;21m",  # 灰色
        logging.INFO: "\x1b[34;21m",  # 蓝色
        logging.WARNING: "\x1b[33;21m",  # 黄色
        logging.ERROR: "\x1b[31;21m",  # 红色
        logging.CRITICAL: "\x1b[31;1m",  # 粗红色
    }
    RESET = "\x1b[0m"

    def __init__(self):
        super().__init__()
        self.base_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    def format(self, record):
        color = self.COLORS.get(record.levelno, "")
        colored_format = f"{color}{self.base_format}{self.RESET}"
        formatter = logging.Formatter(colored_format)
        return formatter.format(record)


def setup_logging():
    """配置日志系统"""
    # 防止重复添加handler
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return root_logger

    # 设置日志级别
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    root_logger.setLevel(log_level)

    # 添加控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(ColorFormatter())
    root_logger.addHandler(console_handler)

    # 生产环境禁用uvicorn访问日志
    if not settings.debug:
        logging.getLogger("uvicorn.access").disabled = True

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """获取指定名称的日志器"""
    return logging.getLogger(name)


# 初始化日志系统
setup_logging()
logger = get_logger(__name__)
