from dotenv import load_dotenv
from pathlib import Path
import os

DEFAULT_DOTENV_PATH = '../config/.env'

def load_env_var(dotenv_path=DEFAULT_DOTENV_PATH):
    """Load environment variables from .env file

    Args:
        dotenv_path (str, optional): Path of .env file. Defaults to DEFAULT_DOTENV_PATH.

    Returns:
        None
    """
    load_dotenv(dotenv_path=DEFAULT_DOTENV_PATH)
    return 


# AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
