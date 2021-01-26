from models.utils import Attribute
from .Model import Model


class ForeignKey(Attribute):
    distant = True

    def __rpy__(self):
        if isinstance(self.get_from, str):
            card = {
                (False, False): "!",
                (False, True): "+",
                (True, False): "?",
                (True, True): "*",
            }[(self.optional, self.multiple)]

            return f"({card}{self.name}[{self.get_from}])"
        else:
            return f">{self.name}"

    @property
    def model(self):
        return Model.__get_model__(self.get_from)

    def get(self, from_instance):
        if isinstance(self.get_from, str):
            model = self.model
            assert model, self.get_from
            result = model.__instances__.where(**{self.get_by: from_instance})
            if self.multiple:
                return result.finalize()
            else:
                return result.first()
        else:
            return self.get_from(from_instance)

    def __init__(self, name, get_from, get_by: str = None, optional: bool = False, multiple: bool = False,
                 on_lazy: bool = False):
        super().__init__(name)
        self.get_from = get_from
        self.get_by = get_by
        self.optional = optional
        self.multiple = multiple
        self.on_lazy = on_lazy
