import logging
import os
from enum import Enum
from pathlib import Path

import dotenv

log = logging.getLogger()

CONFIG_FOLDER = Path.home() / ".mos-moss"
CONFIG_PATH = CONFIG_FOLDER / "config.env"


class ConfigKey(Enum):
    MOSS_KEY = "MOSS_KEY"
    CANVAS_KEY = "CANVAS_KEY"


def set_config(key: ConfigKey, value: str) -> None:
    dotenv.set_key(CONFIG_PATH, key.name, value)
    dotenv.load_dotenv(CONFIG_PATH)


def get_config(key: ConfigKey) -> str:
    return os.getenv(key.name)


def load_keys() -> None:
    if dotenv.load_dotenv(CONFIG_PATH):
        log.info("Config file loaded.")
        return
    log.info(f"No config file found at {CONFIG_PATH}, creating one.")
    CONFIG_FOLDER.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "x") as f:
        f.writelines(f"{k.value}\n" for k in ConfigKey)
