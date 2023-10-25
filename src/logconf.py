import logging
from rich.logging import RichHandler

# Constants for log configuration
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d:%(funcName)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
LOG_FILE_PATH = "/home/and/Dropbox/computing-msc-uea/nlp/axidoc/logs/core_logs.txt"
LOG_LEVEL = logging.DEBUG  # logging.CRITICAL

class CustomLogger(logging.Logger):
    def __init__(self, name, level=LOG_LEVEL):
        super().__init__(name, level)

        # Create and add the formatter and handler for file logging
        formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
        file_handler = logging.FileHandler(LOG_FILE_PATH, mode='a')  # 'a' means append mode
        file_handler.setFormatter(formatter)
        self.addHandler(file_handler)

        # Add delimiter for new runs
        with open(LOG_FILE_PATH, 'a') as f:
            f.write("\n\n============\n\n")

        # Handler for rich console logging
        rich_console_handler = RichHandler(
            level=LOG_LEVEL,
            rich_tracebacks=True,
            markup=True
        )
        self.addHandler(rich_console_handler)

        # Not propagate to root logger
        self.propagate = False

# Replace the default logger class with our custom logger
logging.setLoggerClass(CustomLogger)

def get_logger(name=__name__):
    return logging.getLogger(name)


# You can now use get_logger in all your modules to get the custom logger:
# logger = logconf.get_logger(__name__)
# logger.info("This is an info message.")

