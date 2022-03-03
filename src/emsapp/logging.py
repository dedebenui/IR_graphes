import logging
from logging.handlers import RotatingFileHandler
import pkg_resources

LOG_FILE = pkg_resources.resource_filename("emsapp", "logs/emsapp.log")
ROT_FILE_HANDLER = RotatingFileHandler(LOG_FILE, maxBytes=512000, backupCount=5, encoding="utf-8")


def get_logger(name=None):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    if ROT_FILE_HANDLER not in logger.handlers:
        logger.addHandler(ROT_FILE_HANDLER)
    return logger
