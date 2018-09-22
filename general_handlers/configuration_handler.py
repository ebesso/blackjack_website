from models import Empty
import configparser

def load(section):
    config_obj = configparser.ConfigParser()

    config_obj.read('configuration.ini')
    
    configs = dict(config_obj.items(section))

    configuration = Empty()

    for config in configs:
        configuration.__setattr__(config, configs[config])
    
    return configuration
