import yaml
import config
import logging
import logging.config

__logger = None


def get_logger():
    global __logger

    if __logger is not None:
        return __logger

    with open(config.LOGZ, 'r') as file:
        try:
            log_config = yaml.load(file, Loader=yaml.SafeLoader)
            for i in log_config['handlers']:
                log_config['handlers'][i]['filename'] = str(config.LOGS / log_config['handlers'][i]['filename'])
            logging.config.dictConfig(log_config)
        except yaml.YAMLError as e:
            print('Error loading logger, using default config', e)

    __logger = logging.getLogger(__name__)

    return __logger

