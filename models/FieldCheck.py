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
        if model.h.instances.where(**{field.name: value}).first not in (None, instance):
            return f"Value already existing in the column : {value}"

    @staticmethod
    def is_static(create, **_):
        if not create:
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
