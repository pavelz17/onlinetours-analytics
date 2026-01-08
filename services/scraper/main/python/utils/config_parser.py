import os
import logging
import configparser


logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.propagate = False


class ConfigParser:
    def __init__(self, config_file: str):
        self.parser = configparser.ConfigParser()
        conf_path = os.environ['CONFIG_PATH']
        logger.info(f'Reading config from {conf_path}/{config_file}')
        self.parser.read(f'{conf_path}/{config_file}')

    def get_group(self, section: str):
        return self.parser[section]

    def get_property(self, section: str, prop: str):
        return self.parser[section][prop]
