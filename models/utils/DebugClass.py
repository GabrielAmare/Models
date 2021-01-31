class DebugClass:
    """
        Subclasses of DebugClass can be used to display debug messages easily
    """
    def __init__(self, debug):
        self.debug = debug

    def debug_message(self, message):
        if self.debug:
            print(f"[{self.__class__.__name__}] {message}")
