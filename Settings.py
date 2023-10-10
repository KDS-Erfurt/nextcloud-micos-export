import json
from pathlib import Path
from typing import Optional

from controllogger.enums.log_levels import LogLevels
from pydantic import BaseSettings

settings_filepath = Path("settings.json")


class Settings(BaseSettings):
    dry_run: bool = True
    input_path: Path
    output_path: Path
    on_fail_path: Path
    on_delete_path: Path
    log_filepath: Path
    log_level: LogLevels = LogLevels.WARNING
    log_file_maxsize: int = 1024 * 1024 * 10  # 10MB
    log_file_max_count: int = 5
    move_interval: float = 2
    delete_interval: float = 100
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


settings = Settings()
