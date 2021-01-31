from .FieldError import FieldError


class FieldUpdateError(FieldError):
    def __str__(self):
        return f"[u]{super().__str__()}"
