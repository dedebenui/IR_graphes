import logging

try:
    logging.basicConfig(filename="emsapp.log", encoding="utf-8", level=logging.DEBUG)
except PermissionError:
    import os

    logging.basicConfig(
        filename=os.path.join(os.path.expanduser("~"), "emsapp.log"),
        encoding="utf-8",
        level=logging.DEBUG,
    )


def get_logger(name=None):
    return logging.getLogger(name)
