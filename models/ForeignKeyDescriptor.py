from .AttributeDescriptor import AttributeDescriptor


class ForeignKeyDescriptor(AttributeDescriptor):
    def __init__(self, name, type, get_by: str = None, on_lazy: bool = False, **config):
        """
        :param get_from: if specified (list), it's the set of authorized values for the field
        :param get_by: if specified (tuple of 2 elements, start & step) auto-increment the field value when unspecified
        :param on_lazy: [optional] set a range of authorized values (ex: (0, 1000) )
        """
        config['unique'] = not config.get('multiple', False)
        config['static'] = False
        super().__init__(name, type, **config)
        self.get_from = type
        self.get_by = get_by
        self.on_lazy = on_lazy
