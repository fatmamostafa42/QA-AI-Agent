from functools import lru_cache
from pathlib import Path

import yaml


# Folder that contains models.yaml and settings.yaml
CONFIG_DIR = Path(__file__).resolve().parent


@lru_cache(maxsize=1)
def load_models():
    """
    Load models configuration from models.yaml
    """
    config_file = CONFIG_DIR / "models.yaml"

    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")

    with config_file.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@lru_cache(maxsize=1)
def load_settings():
    """
    Load application settings from settings.yaml
    """
    config_file = CONFIG_DIR / "settings.yaml"

    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")

    with config_file.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)