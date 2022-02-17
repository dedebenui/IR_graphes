SILENCE = True


def handle_debug(msg: str):
    if not SILENCE:
        print(msg)


def handle_info(msg: str):
    if not SILENCE:
        print(msg)


def handle_warning(msg: str):
    if not SILENCE:
        print(msg)


def handle_error(msg: str):
    if not SILENCE:
        print(msg)


def handle_fatal(msg: str):
    if not SILENCE:
        print(msg)
