from .AttributeDescriptor import AttributeDescriptor
from .FieldCheck import FieldCheck
from .utils import Query


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

        self.checks = Query(data=list(self.init_checks()), safe=True)

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
