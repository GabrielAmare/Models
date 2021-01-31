from ..utils.functions import indent


class FieldUpdateError(Exception):
    def __init__(self, field, errors: list):
        self.field = field
        self.errors = errors

    def __bool__(self):
        return any(self.errors)

    def __repr__(self):
        return f"{self.field.name}:\n{indent(self.errors)}"
