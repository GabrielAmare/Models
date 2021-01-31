from ..utils.functions import indent


class ModelError(Exception):
    def __init__(self, model, errors: list):
        self.model = model
        self.errors = errors

    def __bool__(self):
        return any(self.errors)

    def __repr__(self):
        return f"{self.model.__name__}:\n{indent(self.errors)}"
