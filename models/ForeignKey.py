from .utils import Attribute
from .Model import Model
from .ForeignKeyDescriptor import ForeignKeyDescriptor


class ForeignKey(Attribute):
    distant = True

    def __rpy__(self):
        return self.__descriptor__.to_rpy()

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
                 on_lazy: bool = False, private: bool = False):
        super().__init__(name)

        self.__descriptor__ = ForeignKeyDescriptor(
            # BASE
            name=name,
            optional=optional,
            multiple=multiple,
            private=private,
            # FK
            get_from=get_from,
            get_by=get_by,
            on_lazy=on_lazy
        )

        self.get_from = get_from
        self.get_by = get_by
        self.optional = optional
        self.multiple = multiple
        self.on_lazy = on_lazy

    def __call__(self, model):
        result = super().__call__(model)

        def emit_append(owner):
            Model.__events__.emit(f'{model.__name__}/{getattr(owner, self.get_by).uid}/append/{self.name}', owner)

        Model.__events__.on(f'{self.get_from}/#/create', emit_append)

        return result
