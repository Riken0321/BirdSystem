import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    # 定义不同的日志分类
    log_categories = {
        "tortoise": {
            "file_path": "logs/tortoise.log",
            "max_bytes": 10240,
            "backup_count": 5
        },
        "requests": {
            "file_path": "logs/requests.log",
            "max_bytes": 10240,
            "backup_count": 5
        },
        # 可以根据需要添加更多分类
    }

    for category, config in log_categories.items():
        # 获取对应分类的日志记录器
        logger = logging.getLogger(category)
        logger.setLevel(logging.DEBUG)

        # 创建文件处理器，设置日志文件大小和备份数量
        file_handler = RotatingFileHandler(
            config["file_path"],
            maxBytes=config["max_bytes"],
            backupCount=config["backup_count"]
        )
        file_handler.setLevel(logging.DEBUG)

        # 定义日志格式
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)

        # 将文件处理器添加到日志记录器