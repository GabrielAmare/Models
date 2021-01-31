def indent(s, prefix: str = "  ", suffix: str = ""):
    if isinstance(s, str):
        return "\n".join(prefix + line + suffix for line in s.split("\n"))
    elif hasattr(s, '__iter__'):
        return indent("\n".join(map(str, s)), prefix, suffix)
    else:
        raise Exception(f"Wrong argument type for s: {type(s)}, expected (str, iterable)")
