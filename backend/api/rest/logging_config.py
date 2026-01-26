import logging
import logging.config
import os


def setup_logging(level: str = "INFO"):
    """애플리케이션 로깅을 설정합니다.

    Args:
        level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # 로그 디렉토리 생성
    os.makedirs("logs", exist_ok=True)

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
            "detailed": {
                "format": """
                %(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d
                - %(funcName)s - %(message)s
                """,
            },
            "json": {
                "format": """{
                    "timestamp": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s",
                    "message": "%(message)s", "file": "%(filename)s", "line": %(lineno)d
                }""",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": level,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "detailed",
                "filename": "logs/app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "level": level,
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "json",
                "filename": "logs/error.log",
                "maxBytes": 10485760,
                "backupCount": 10,
                "level": "ERROR",
            },
        },
        "loggers": {
            "": {  # root logger
                "handlers": ["console", "file"],
                "level": level,
                "propagate": False,
            },
            "uvicorn": {
                "handlers": ["console"],
                "level": level,
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["error_file"],
                "level": "ERROR",
                "propagate": False,
            },
            "app": {
                "handlers": ["console", "file", "error_file"],
                "level": level,
                "propagate": False,
            },
        },
    }

    logging.config.dictConfig(logging_config)
