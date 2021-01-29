from .AttributeDescriptor import AttributeDescriptor


class ForeignKeyDescriptor(AttributeDescriptor):
    def __init__(self, name, get_from, get_by: str = None, on_lazy: bool = False, **config):
        """
        :param get_from: if specified (list), it's the set of authorized values for the field
        :param get_by: if specified (tuple of 2 elements, start & step) auto-increment the field value when unspecified
        :param on_lazy: [optional] set a range of authorized values (ex: (0, 1000) )
        """
        super().__init__(name, f"{get_from}.{get_by}", unique=not config.get('multiple', False), static=False, **config)
        self.get_from = get_from
        self.get_by = get_by
        self.on_lazy = on_lazy
