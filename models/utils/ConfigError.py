class ConfigError(Exception):
    def __init__(self, model, config_errors):
        self.model = model
        self.config_errors = config_errors

    def __str__(self):
        lines = [f"{self.model.__name__} :"]
        for name, errors in self.config_errors.items():
            l_lines = [f"  {name} :"]
            for error in errors:
                l_lines.append(f"    {error}")
            if len(l_lines) > 1:
                lines.extend(l_lines)
        return "\n" + "\n".join(lines)
