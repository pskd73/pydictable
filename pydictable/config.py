class ConfigDict:
    def __init__(self, str_strip_whitespace=None):
        self.str_strip_whitespace = str_strip_whitespace


def merge_configs(conf1: ConfigDict, conf2: ConfigDict) -> ConfigDict:
    config_values = {}
    for config in (conf1, conf2):
        for attr in vars(config):
            if not attr.startswith('_') and (value := getattr(config, attr)) is not None:
                config_values[attr] = value
    return ConfigDict(**config_values)
