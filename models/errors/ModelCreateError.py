from .ModelError import ModelError


class ModelCreateError(ModelError):
    def __str__(self):
        return f"\n[c]{super().__str__()}"
