import logging
import os
from config.settings import ENABLE_LOGGING, LOG_LEVEL

LOG_FILE_PATH = "data/deskguardian.log"

class Logger:
    """
    Central logging utility.
    Supports:
    - Console logging
    - File logging
    - Log levels
    """

    _initialized = False

    @staticmethod
    def _initialize():
        if Logger._initialized:
            return

        os.makedirs("data", exist_ok=True)

        logging.basicConfig(
            level=getattr(logging, LOG_LEVEL),
            format="%(asctime)s | %(levelname)s | %(message)s",
            handlers=[
                logging.FileHandler(LOG_FILE_PATH),
                logging.StreamHandler()
            ]
        )

        Logger._initialized = True

    @staticmethod
    def debug(message):
        if ENABLE_LOGGING:
            Logger._initialize()
            logging.debug(message)

    @staticmethod
    def info(message):
        if ENABLE_LOGGING:
            Logger._initialize()
            logging.info(message)

    @staticmethod
    def warning(message):
        if ENABLE_LOGGING:
            Logger._initialize()
            logging.warning(message)

    @staticmethod
    def error(message):
        if ENABLE_LOGGING:
            Logger._initialize()
            logging.error(message)
