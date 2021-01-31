from .FieldError import FieldError


class FieldCreateError(FieldError):
    def __str__(self):
        return f"[c]{super().__str__()}"
