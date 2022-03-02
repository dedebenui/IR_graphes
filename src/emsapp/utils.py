"""python convenience objects that have nothing to do with the topic of the project"""

import inspect


class AutoList:
    """
    Descriptor that guaranties to return a list, even if only one element it assigned

    Example
    -------
    ```
    class A:
        x: list[int] = AutoList(int)

    a = A()
    a.x = 4
    print(a.x) # [4]
    ```
    """

    def __init__(self, tpe: type, optional=False):
        self.optional = optional
        self.tpe = tpe

    def __set_name__(self, owner, name):
        self.name = "_" + name
        try:
            self.owner = owner.__name__
        except AttributeError:
            self.owner = ""

    def __get__(self, obj, objtype=None):
        return getattr(obj, self.name)

    def __set__(self, obj, value):
        if value is None and not self.optional:
            raise ValueError(f"{self.owner}.{self.name[1:]} is not optional")
        setattr(obj, self.name, [value] if isinstance(value, self.tpe) else value)


def auto_repr(cls):
    def __repr__(self) -> str:
        anots = {}
        for base_cls in inspect.getmro(cls)[::-1]:
            try:
                anots.update(base_cls.__annotations__)
            except AttributeError:
                continue

        return f"{cls.__name__}({', '.join('{}={}'.format(k, getattr(self, k)) for k in anots)})"

    cls.__repr__ = __repr__
    return cls
