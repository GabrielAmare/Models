from .AttributeDescriptor import AttributeDescriptor


class FieldCheck:
    @staticmethod
    def at_least_one_element(value, **_):
        if not value:
            return "At least 1 element required"

    @staticmethod
    def not_none(value, **_):
        if value is None:
            return "Value is not optional"

    @staticmethod
    def valid_type(field, value, **_):
        if not isinstance(value, field.dtype):
            return f"The value {value} should be typed as {field.type_}"

    @staticmethod
    def is_unique(model, instance, field, value, **_):
        if model.__instances__.where(**{field.name: value}).first not in (None, instance):
            return f"Value already existing in the column : {value}"

    @staticmethod
    def is_static(mode, **_):
        if mode == 'update':
            return f"The value can't be modified (static field)"

    @staticmethod
    def in_values(field, value, **_):
        if value not in field.values:
            return f"The value {value} doesn't belong to the list of authorized values"

    @staticmethod
    def in_range(field, value, **_):
        if not field.range[0] <= value <= field.range[1]:
            return f"The value {value} doesn't belong to the range {field.range}"

    @staticmethod
    def in_length(field, value, **_):
        if not field.length[0] <= len(value) <= field.length[1]:
            f"The value length {len(value)} doesn't belong to the length range {field.length}"


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

        self.__checks__ = list(self.init_checks())

    def init_checks(self):
        """
        Yield all the necessary check functions that field needs to perform during the value check
        :param field: a Field instance
        :return: A generator of the check functions the field needs to perform
        """
        if not self.optional:
            yield FieldCheck.valid_type

            if self.multiple:
                yield FieldCheck.at_least_one_element
            else:
                yield FieldCheck.not_none

            if self.unique:
                yield FieldCheck.is_unique

            if self.static:
                yield FieldCheck.is_static

            if self.values:
                yield FieldCheck.in_values

            if self.range:
                yield FieldCheck.in_range

            if self.length:
                yield FieldCheck.in_length
