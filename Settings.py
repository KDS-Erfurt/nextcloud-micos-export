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
    input_path: Path
    output_path: Path
    on_fail_path: Path
    log_filepath: Path
    log_level: LogLevels = LogLevels.warning
    log_file_maxsize: int = 10737418240  # 10MB
    log_file_max_count: int = 5
    loop_delay: float = 2
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
