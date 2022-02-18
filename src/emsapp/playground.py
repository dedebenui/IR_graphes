

class ValueErrorSuppressor:
    def __enter__(self):
        ...

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type is ValueError:
            print(exc_value)
            return True


def lol(s):
    with ValueErrorSuppressor():
        x = int(s)
        return x
    return 0


def lol2(x):
    with ValueErrorSuppressor():
        try:
            y = int(x)
            return 1/y
        except ValueError:
            print("deeper catch")


print(lol(5))
print(lol("lol"))
print(lol2("lol"))
print(lol2(0))