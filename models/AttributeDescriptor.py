class AttributeDescriptor:
    to_rpy_card = {(False, False): "!", (False, True): "+", (True, False): "?", (True, True): "*"}
    from_rpy_card = {"!": (False, False), "+": (False, True), "?": (True, False), "*": (True, True)}

    symbol_unique = '-u'
    symbol_static = '-p'
    symbol_private = '-s'

    name: str
    type: str
    optional: bool
    multiple: bool
    unique: bool
    private: bool
    static: bool

    def __init__(self, name: str, type: str, optional: bool = False, multiple: bool = False, unique: bool = False,
                 private: bool = False, static: bool = False):
        """
        :param name: The name of the field (expected as string)
        :param type: The type of the field value (expected as string)
        :param optional: if True, the field is not required
        :param multiple: if True, the field handle a list of values
        :param unique: if True, for a given table, the same value cannot appears twice
        :param private: if True, the field value is filter out from the result of the $.to_dict method
        :param static: if True, the field value can only be set at the object creation (making the field immutable)
        """
        self.name = name
        self.type = type
        self.optional = optional
        self.multiple = multiple
        self.unique = unique
        self.private = private
        self.static = static

    def to_rpy(self):
        """Return the Field Descriptor in rpy format"""
        card = self.to_rpy_card[(self.optional, self.multiple)]

        isUnique = f" {self.symbol_unique}" if self.unique else ""
        isStatic = f" {self.symbol_static}" if self.static else ""
        isPrivate = f" {self.symbol_private}" if self.private else ""

        return f"{card}{self.name}[{self.type}]{isUnique}{isStatic}{isPrivate}"

    @classmethod
    def from_rpy(cls, rpy: str):
        """Return a Field Descriptor from a rpy formatted string"""
        optional, multiple = cls.from_rpy_card[rpy[0]]

        name = rpy[1:].split('[', 1)[0]

        type = rpy.split('[', 1)[1].split(']', 1)[0]

        unique = cls.symbol_unique in rpy
        private = cls.symbol_static in rpy
        static = cls.symbol_private in rpy

        return cls(name=name, type=type, optional=optional, multiple=multiple, unique=unique, private=private,
                   static=static)
