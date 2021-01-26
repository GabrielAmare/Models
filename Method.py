from models.utils import Attribute


class Method(Attribute):
    distant = True

    def __rpy__(self):
        return f"~{self.name}()"

    def __init__(self, name, method=None):
        if hasattr(name, '__call__') and method is None:
            method = name
            name = method.__name__
        super().__init__(name)
        self.method = method

    def get(self, instance):
        return lambda *args, **kwargs: self.method(instance, *args, **kwargs)
