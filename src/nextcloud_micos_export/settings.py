from pathlib import Path
import sys

from pydantic import Field, DirectoryPath, ValidationError
from wiederverwendbar.logger import LoggerSettings
from wiederverwendbar.pydantic import FileConfig, ModelSingleton
from wiederverwendbar.singleton import Singleton

SETTINGS_FILE_NAME: str = "settings.json"
SETTINGS_LOOKUP_PATHS: list[Path] = [
    Path("."),
    Path("/usr/local/etc/nextcloud-micos-export"),
    Path("/usr/local/opt/nextcloud-micos-export"),
    Path("/etc/nextcloud-micos-export"),
    Path("/opt/nextcloud-micos-export")
]


class Settings(FileConfig, LoggerSettings, metaclass=ModelSingleton):
    dry_run: bool = Field(default=False, description="Dry run.")
    input_path: DirectoryPath = Field(default=..., description="Path to input directory.", exists=True)
    output_path: DirectoryPath = Field(default=..., description="Path to output directory.", exists=True)
    on_fail_path: DirectoryPath = Field(default=..., description="Path to on_fail directory.", exists=True)
    on_delete_path: DirectoryPath = Field(default=..., description="Path to on_delete directory.", exists=True)
    move_interval: int = Field(default=2, description="Interval in seconds between move operations. Default: 2 seconds")
    delete_interval: int = Field(default=100, description="Interval in seconds between delete operations. Default: 100 seconds")
    delete_max_age: int = Field(default=2 * 365 * 24 * 60 * 60, description="Max age in seconds for delete operations. Default: 2 years")
    timezone: str = Field(default="Europe/Berlin", description="Timezone for cron jobs. Default: Europe/Berlin")
    cleanup_hour: int = Field(default=..., description="Hour of the day to cleanup. Default: 22")
    cleanup_minute: int = Field(default=..., description="Minute of the hour to cleanup. Default: 0")
    pid_file_name: str = Field(default="nextcloud_micos_export", description="Name of the pid file.")
    pid_file_path: Path = Field(default=Path("/tmp"), description="Path to pid file.", exists=True)
    skip_zeros_on_username: bool = Field(default=False, description="Skip zeros on username.")
    nextcloud_db_host: str = Field(default="localhost", description="Host of the nextcloud database.")
    nextcloud_db_port: int = Field(default=3306, description="Port of the nextcloud database.")
    nextcloud_db_name: str = Field(default="nextcloud", description="Name of the nextcloud database.")
    nextcloud_db_user: str = Field(default="lohnexport", description="User of the nextcloud database.")
    nextcloud_db_password: str = Field(default=..., description="Password of the nextcloud database.")


def settings() -> Settings:
    try:
        return Singleton.get_by_type(Settings)
    except RuntimeError:
        try:
            s = None
            for path in SETTINGS_LOOKUP_PATHS:
                file_path = path / SETTINGS_FILE_NAME
                if not file_path.is_file():
                    continue
                s = Settings(file_path=file_path, file_must_exist=True, init=True)
                break
            if s is None:
                raise FileNotFoundError(f"No '{SETTINGS_FILE_NAME}' file found. Possible paths:\n"
                                        f"{f'{chr(10)}'.join([str(path.absolute() / SETTINGS_FILE_NAME) for path in SETTINGS_LOOKUP_PATHS])}")
            return s
        except FileNotFoundError as e:
            print(e)
            sys.exit(1)
        except ValidationError as e:
            print(e)
            sys.exit(1)
