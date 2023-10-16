import json
import sys
from pathlib import Path

import pydantic
from controllogger.enums.log_levels import LogLevels
from pydantic import BaseModel, Field, DirectoryPath

settings_filepath = Path("settings.json")


class Settings(BaseModel):
    dry_run: bool = True
    input_path: DirectoryPath = Field(..., description="Path to input directory.", exists=True)
    output_path: DirectoryPath = Field(..., description="Path to output directory.", exists=True)
    on_fail_path: DirectoryPath = Field(..., description="Path to on_fail directory.", exists=True)
    on_delete_path: DirectoryPath = Field(..., description="Path to on_delete directory.", exists=True)
    log_filepath: DirectoryPath = Field(..., description="Path to log file.", exists=True)
    log_level: LogLevels = LogLevels.WARNING
    log_file_maxsize: int = 1024 * 1024 * 10  # 10MB
    log_file_max_count: int = 5
    move_interval: float = 2
    delete_interval: float = 100
    delete_max_age: int = 2 * 365 * 24 * 60 * 60  # 2 years
    pip_file: Path = Path("/tmp/nextcloudmicosexport.pip")
    skip_zeros_on_username: bool = False

    class Config:
        use_enum_values = True


# check if settings file exists
if not settings_filepath.is_file():
    print(f"Settings file '{settings_filepath}' not found. -> Create default settings file.")
    print(f"Please edit settings file '{settings_filepath}' and restart.")
    default_settings_dict = {
        "dry_run": True,
        "input_path": None,
        "output_path": None,
        "on_fail_path": None,
        "on_delete_path": None,
        "log_filepath": None,
        "log_level": 40,
        "log_file_maxsize": 1024 * 1024 * 10,  # 10MB
        "log_file_max_count": 5,
        "move_interval": 2,
        "delete_interval": 100,
        "delete_max_age": 2 * 365 * 24 * 60 * 60,  # 2 years
        "pip_file": "/tmp/nextcloudmicosexport.pip",
        "skip_zeros_on_username": False
    }
    with open(settings_filepath, "w") as file:
        json.dump(default_settings_dict, file, indent=4)
    sys.exit(1)
else:
    try:
        settings = Settings.parse_file(settings_filepath)
    except pydantic.ValidationError as e:
        print(f"Can't read Settings file '{settings_filepath}'.\n{e}")
        sys.exit(1)
