"""统一日志配置"""

import logging
import sys
from pathlib import Path

from app.config import BASE_DIR, LOG_LEVEL


def setup_logging(name: str = "copilot") -> logging.Logger:
    log_dir = BASE_DIR / "logs"
    log_dir.mkdir(exist_ok=True)

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    logger.addHandler(console)

    file_handler = logging.FileHandler(log_dir / "copilot.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
