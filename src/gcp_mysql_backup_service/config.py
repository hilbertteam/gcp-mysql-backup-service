import logging.config
import os
from dataclasses import dataclass
from typing import Dict

from ruamel.yaml import YAML, yaml_object

from gcp_mysql_backup_service.exceptions import ConfigurationError

yaml = YAML()


@yaml_object(yaml)
@dataclass
class LoggingConfig:
    handlers: Dict[str, Dict]

    @classmethod
    def load(cls, filename: str = 'logging-config.yml') -> 'LoggingConfig':
        current_workdir = os.path.join(os.getcwd())
        filename = os.path.join(current_workdir, filename)

        try:
            with open(filename, 'r') as file:
                config = yaml.load(file.read())
                return config
        except (FileNotFoundError, IsADirectoryError):
            raise ConfigurationError(f'Logging config file "{filename}" not found, exiting!')

    def apply(self):
        logging.config.dictConfig(self.__dict__)
