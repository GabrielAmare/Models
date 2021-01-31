from .ModelError import ModelError


class ModelUpdateError(ModelError):
    def __str__(self):
        return f"\n[u]{super().__str__()}"
