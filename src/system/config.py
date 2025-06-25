import os
import json
from src.exceptions.ConfigError import ConfigError

class Config:
    def __init__(self, config_filename='config.json'):
        self.recipy_directory = None
        self.cache = None
        self._load_config(config_filename)

    def _load_config(self, filename):
        """Loads the contents of the config file into memory - different fields
        Might throw ConfigError"""
        config_path = os.path.join(os.getcwd(), filename)
        if not os.path.exists(config_path):
            raise ConfigError(f"Config file '{filename}' not found in current working directory.")

        try:
            with open(config_path, "r", encoding='utf-8') as f:
                data = json.load(f)

            self.recipy_directory = data.get("recipy_directory")
            if not self.recipy_directory:
                raise ConfigError("Missing 'recipy_directory' field in config file.")
            self.cache = data.get("cache_file")

        except json.JSONDecodeError:
            raise ConfigError("Invalid JSON format in config file.")
        except Exception as e:
            raise ConfigError(f"Error loading config: {e}")