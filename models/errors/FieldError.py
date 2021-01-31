from ..utils.functions import indent


class FieldError(Exception):
    def __init__(self, field, errors: list):
        self.field = field
        self.errors = errors

    def __bool__(self):
        return any(self.errors)

    def __str__(self):
        return f"{self.field.name}:\n{indent(self.errors, '  > ')}\n"
