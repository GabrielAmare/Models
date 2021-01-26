class Attribute:
    distant = False
    private = False
    on_lazy = False
    model = None

    def __init__(self, name):
        self.name = name

    def __rpy__(self):
        raise NotImplementedError

    def get(self, instance):
        raise NotImplementedError

    def __call__(self, model):
        model.__attributes__.append(self)
        return model
