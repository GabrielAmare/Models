from .utils import Query


class FORMATS:
    def __init__(self, model):
        self.model = model
        self.customs = {}

    def _isModel(self, obj):
        return obj in self.model.__models__

    # SUBFORMATS

    @staticmethod
    def _parse_model_subformat(attribute, subformat, fill: bool = False):
        return attribute.model.__formats__.deserialize(subformat, fill)

    def _parse_EAGER_subformat(self, attribute, fill: bool = False):
        if self._isModel(attribute.dtype):
            return self._parse_model_subformat(attribute, "EAGER", fill)
        else:
            return True

    def _parse_LAZY_subformat(self, attribute, fill: bool = False):
        if attribute.__class__.__name__ != "Field":
            return False if fill else None
        elif self._isModel(attribute.dtype):
            return self._parse_model_subformat(attribute, "LAZY", fill)
        else:
            return True

    def _parse_dict_subformat(self, attribute, format, fill: bool = False):
        subformat = format.get(attribute.name)

        if attribute.__class__.__name__ == "ForeignKey":
            return self._parse_model_subformat(attribute, subformat, fill)
        elif attribute.__class__.__name__ == "Field" and self._isModel(attribute.dtype):
            return self._parse_model_subformat(attribute, subformat, fill)
        elif subformat is True:
            return True
        elif subformat in (False, None):
            return False if fill else None
        else:
            raise Exception(f"Invalid subformat {subformat} for {self.model.__name__}.{attribute.name}!")

    # QUERY

    def _parse_EAGER(self, fill: bool = False) -> Query:
        return self.model.__attributes__.map(
            lambda attribute: (attribute.name, self._parse_EAGER_subformat(attribute, fill))
        )

    def _parse_LAZY(self, fill: bool = False) -> Query:
        return self.model.__attributes__ \
            .map(lambda attribute: (attribute.name, self._parse_LAZY_subformat(attribute, fill)))

    def _parse_str(self, format: str, fill: bool = False) -> Query:
        if format == "EAGER":
            return self._parse_EAGER(fill)
        elif format == "LAZY":
            return self._parse_LAZY(fill)
        elif format in self.customs:
            return self._parse_query(self.customs[format], fill)
        else:
            raise Exception(f"{self.model.__name__}.__formats__ doesn't include {format}")

    def _parse_dict(self, format: dict, fill: bool = False) -> Query:
        return self.model.__attributes__.map(
            lambda attribute: (attribute.name, self._parse_dict_subformat(attribute, format, fill))
        )

    def _parse_query(self, format, fill: bool = False) -> Query:
        if isinstance(format, str):
            return self._parse_str(format, fill)
        elif isinstance(format, dict):
            return self._parse_dict(format, fill)
        else:
            raise Exception(f"Invalid format {format} !")

    # DICT

    def parse(self, format, fill=False) -> dict:
        return self._parse_query(format, fill).filter(lambda e: e[1] is None).dict()
