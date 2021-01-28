import re


class EventKey:
    std_key = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")

    @classmethod
    def parse(cls, obj):
        if isinstance(obj, cls):
            return obj
        elif isinstance(obj, str):
            if obj.startswith('<') and obj.endswith('>'):
                l = False
                obj = obj[1:-1]
            else:
                l = True

            if obj == '*':
                k = '*'
                t = str
            elif obj == '#':
                k = '*'
                t = int
            elif obj.count(':') == 1:
                k, t = obj.split(':', 1)
                t = {'int': int, 'str': str, 'float': float, 'bool': bool}[t]
            else:
                k = obj
                t = str

            return cls(k, t, l)
        else:
            raise Exception(f"Unable to parse {obj.__class__.__name__} into {cls.__name__}")

    def match(self, other):
        other = EventKey.parse(other)
        assert other.litteral
        if self.key == '*':
            if self.litteral:
                return [], {}
            else:
                return [self.type(other.key)], {}
        elif not self.litteral:
            try:
                return [], {self.key: self.type(other.key)}
            except:
                return None
        elif self.key == other.key:
            return [], {}
        else:
            return None

    def __init__(self, key, type, litteral):
        self.key = key
        self.type = type
        self.litteral = litteral

    def __str__(self):
        result = self.key

        if self.type is not str:
            result += f":{self.type.__name__}"

        if result == '*:int':
            result = '#'

        if not self.litteral:
            result = f"<{result}>"

        return result

    def __repr__(self):
        return f"({self.key}, {self.type.__name__}, {int(self.litteral)})"


class Event:
    sep = "/"

    @classmethod
    def parse(cls, obj):
        if isinstance(obj, cls):
            return obj
        elif isinstance(obj, str):
            keys = obj.split(Event.sep)
            return cls(*keys)
        else:
            raise Exception(f"Unable to parse {obj.__class__.__name__} into {cls.__name__}")

    def match(self, other):
        other = Event.parse(other)
        if str(self) == '*':
            return [str(other)], {}

        if len(self.keys) != len(other.keys):
            return None

        args, kwargs = [], {}
        for k1, k2 in zip(self.keys, other.keys):
            if match := k1.match(k2):
                l_args, l_kwargs = match
                args.extend(l_args)
                kwargs.update(l_kwargs)
            else:
                return None

        return args, kwargs

    def __init__(self, *keys):
        self.keys = tuple(map(EventKey.parse, keys))

    def __str__(self):
        return "/".join(map(str, self.keys))

    def __repr__(self):
        return f"{self.__class__.__name__}(" + ", ".join(map(repr, self.keys)) + ")"


class EventManager:
    events = {}

    @classmethod
    def parse_event(cls, event: str):
        return Event.parse(event)

    @classmethod
    def match(cls, event, r_event, value):
        if r_event == '*':
            return [event, value], {}
        else:
            return None

    @classmethod
    def emit(cls, event, value):
        event = cls.parse_event(event)
        # print('--emit :', repr(event))
        for r_event, callbacks in cls.events.copy().items():
            if match := r_event.match(event):
                args, kwargs = match
                for callback in callbacks:
                    callback(*args, value, **kwargs)

    @classmethod
    def on(cls, event, callback):
        event = cls.parse_event(event)
        # print('--on   :', repr(event))
        cls.events.setdefault(event, [])
        cls.events[event].append(callback)

        def unsubscribe():
            callbacks = cls.events[event]
            if callback in callbacks:
                callbacks.remove(callback)

        return unsubscribe


if __name__ == '__main__':
    EventManager.on('*', lambda event, value: print(f"[*] {event} -> {value}"))

    EventManager.on('test/3', print)
    EventManager.on('<name>/<uid:int>', lambda *args, **kwargs: print(args, kwargs))

    EventManager.emit('test/3', "coucou")
