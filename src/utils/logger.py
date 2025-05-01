import logging
from logging.handlers import RotatingFileHandler
import sys
from datetime import datetime
from .config import config

class LuvlLogger:
    """Custom logger for LuvlToolGen"""

    def __init__(self):
        # Create logs directory if it doesn't exist
        self.logs_dir = config.logs_dir
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Create logger
        self.logger = logging.getLogger('LuvlToolGen')
        self.logger.setLevel(logging.DEBUG if config.debug else logging.INFO)

        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()

        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s - %(message)s '
            '(%(filename)s:%(lineno)d)'
        )

        console_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s'
        )

        # File handler (with rotation)
        log_file = self.logs_dir / f"luvltoolgen_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.INFO)

        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def debug(self, message: str, *args, **kwargs):
        self.logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs):
        self.logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        self.logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        self.logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs):
        self.logger.critical(message, *args, **kwargs)

    def exception(self, message: str, *args, **kwargs):
        self.logger.exception(message, *args, **kwargs)

# Create global logger instance
logger = LuvlLogger()
