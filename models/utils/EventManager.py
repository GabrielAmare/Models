class EventManager:
    def __init__(self, piped=None):
        self.callbacks = {}
        self.piped = piped

    def on(self, event, function):
        self.callbacks.setdefault(event, [])
        self.callbacks[event].append(function)
        return lambda: self.callbacks[event].remove(function)

    def emit(self, event, *args, **kwargs):
        for function in self.callbacks.get(event, []):
            function(*args, **kwargs)
        for function in self.callbacks.get('*', []):
            function(event, *args, **kwargs)
        if self.piped:
            self.piped.emit(event, *args, **kwargs)
