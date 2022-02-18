import logging

logging.basicConfig(filename="emsapp.log", encoding="utf-8", level=logging.DEBUG)

def get_logger(name = None):
    return logging.getLogger(name)
