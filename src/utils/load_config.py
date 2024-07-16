"""Utility function to read configuration
    
"""

import yaml

DEFAULT_CONFIG_PATH = '../config/config.yml'

def load_config(config_path=DEFAULT_CONFIG_PATH):
    """Load configurations from config yaml file

    Args:
        config_path (str, optional): Path of config yaml file. Defaults to DEFAULT_CONFIG_PATH.

    Returns:
        config (dict) : Dictionary of configurations
    """
    with open(config_path, "r") as config_file:
        config = yaml.safe_load(config_file)
    return config