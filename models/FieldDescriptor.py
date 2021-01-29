from .AttributeDescriptor import AttributeDescriptor


class FieldDescriptor(AttributeDescriptor):
    def __init__(self, name, type, values=None, increment=None, range=None, length=None, default=None, encrypt=None,
                 **config):
        """
        :param values: if specified (list), it's the set of authorized values for the field
        :param increment: if specified (tuple of 2 elements, start & step) auto-increment the field value when unspecified
        :param range: [optional] set a range of authorized values (ex: (0, 1000) )
        :param length: [optional] set a range of autorized length for the values
        :param default: [optional] either a default value, or a default value function (takes the model as argument)
        """
        super().__init__(name, type, **config)
        self.range = range
        self.length = (length, length) if isinstance(length, int) else length
        self.default = default
        self.encrypt = encrypt
        self.values = values
        self.increment = increment
