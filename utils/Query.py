class Query:
    FILTER = "FILTER"
    KEEP = "KEEP"
    MAP = "MAP"

    def __init__(self, data: list = None, safe: bool = False):
        """

        :param data: The original data of the query
        :param safe: If True, means that the Query remains unchanged,
                     when operation is queried on it, it will return a copy instead of self
        """
        if data is None:
            data = []
        self.data = data
        self.funcs = []
        self._safe = safe

    def __iter__(self):
        for item in self.data:
            for tag, func in self.funcs:
                if tag == self.MAP:
                    item = func(item)
                elif tag == self.FILTER:
                    if func(item):
                        break
                elif tag == self.KEEP:
                    if not func(item):
                        break
                else:
                    raise Exception(f"Query.__iter__() : Invalid tag {tag}")
            else:
                yield item

    def append(self, obj):
        """self.data.append(obj)"""
        self.data.append(obj)

    def remove(self, obj):
        """self.data.remove(obj)"""
        self.data.remove(obj)

    def replace(self, old, new):
        """
            Replace the ``old`` item by the ``new`` one
        :param old: The old item
        :param new: The new one
        :return: None
        """
        index = self.data.index(old)
        self.data[index] = new

    @property
    def first(self):
        """Return the first item found in the query"""
        for obj in self:
            return obj

    @property
    def last(self):
        """Return the last item found in the query"""
        obj = None
        for obj in self:
            pass
        return obj

    def copy(self, safe: bool = None):
        """
            Return a copy of 'self'
        :param safe: If None, use the same 'safe' value as 'self', else it's the 'safe' value of the copy
        :return: Query
        """
        if safe is None:
            safe = self._safe
        return self.__class__(
            data=self,
            safe=self._safe if safe is None else safe
        )

    def _apply(self, tag, function):
        query = self.copy(safe=False) if self._safe else self
        query.funcs.append((tag, function))
        return query

    def filter(self, function):
        """Filter the items of the query using criteria ``function``"""
        return self._apply(self.FILTER, function)

    def keep(self, function):
        """Keep the items of the query using criteria ``function``"""
        return self._apply(self.KEEP, function)

    def map(self, function):
        """Map this items of the query using ``function``"""
        return self._apply(self.MAP, function)

    def where(self, **config):
        """Filter the items using a ``config`` dict, where attributes of the items should be equal to their pair in the config"""
        return self.keep(lambda obj: all(getattr(obj, key) == val for key, val in config.items()))

    def getattr(self, name):
        """Map the items by getting their attribute ``name``"""
        return self.map(lambda obj: getattr(obj, name))

    def call(self, *args, **kwargs):
        return self.map(lambda obj: obj(*args, **kwargs))

    def method(self, name, *args, **kwargs):
        return self.getattr(name).call(*args, **kwargs)

    def getitem(self, name):
        """Map the items by getting their item ``name``"""
        return self.map(lambda obj: obj[name])

    def sorted(self, function):
        return sorted(self, key=function)

    def max(self, default=0):
        return max(self, default=default)

    def min(self, default=0):
        return min(self, default=default)

    def sum(self, default=0):
        return sum(self, default)

    def list(self):
        return list(self)

    def tuple(self):
        return tuple(self)

    def dict(self):
        return dict(self)

    def finalize(self, safe=None):
        return self.__class__(data=self.list(), safe=self._safe if safe is None else safe)

    def safe(self):
        self._safe = True
        return self
