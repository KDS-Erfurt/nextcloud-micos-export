import json
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseSettings

settings_filepath = Path("settings.json")


class LogLevels(str, Enum):
    debug = 'DEBUG'
    info = 'INFO'
    warning = 'WARNING'
    error = 'ERROR'


class Settings(BaseSettings):
    version: str = "v0.2"
    dry_run: bool = False
    input_path: Path = "/mnt/Lohn/"
    output_path: Path = "/var/www/nextcloud/data"
    on_fail_path: Path = "/mnt/Lohn/fail"
    log_filepath: Path = "/home/schliwaadm/log.txt"
    log_level: LogLevels = LogLevels.debug
    log_file_maxsize: int = 10737418240  # 10MB
    log_file_max_count: int = 5
    move_interval: float = 2
    delete_interval: float = 10
    delete_max_age: int = 2 * 365 * 24 * 60 * 60  # 2 years
    pip_file: Path = Path("/tmp/ddg_micos_export.pip")

    def __init__(self):
        settings_data: Optional[dict] = None
        if settings_filepath.is_file():
            try:
                with open(settings_filepath, "r") as file:
                    settings_data = json.load(file)
            except json.JSONDecodeError as e:
                print(f"Can't read Settings file '{settings_filepath}'.\n{e}")
                settings_data = None
        else:
            print(f"Settings file '{settings_filepath}' not found.")
        if type(settings_data) == dict:
            super().__init__(**settings_data)
        else:
            super().__init__()

    class Config:
        use_enum_values = True
