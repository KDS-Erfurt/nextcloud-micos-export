from pathlib import Path

from pydantic import Field, DirectoryPath
from wiederverwendbar.logger import LoggerSettings
from wiederverwendbar.pydantic.file_config import FileConfig
from wiederverwendbar.singleton import Singleton


class Settings(FileConfig, LoggerSettings, metaclass=Singleton):
    dry_run: bool = True
    input_path: DirectoryPath = Field(..., description="Path to input directory.", exists=True)
    output_path: DirectoryPath = Field(..., description="Path to output directory.", exists=True)
    on_fail_path: DirectoryPath = Field(..., description="Path to on_fail directory.", exists=True)
    on_delete_path: DirectoryPath = Field(..., description="Path to on_delete directory.", exists=True)
    move_interval: float = Field(2, description="Interval in seconds between move operations. Default: 2 seconds")
    delete_interval: float = Field(100, description="Interval in seconds between delete operations. Default: 100 seconds")
    delete_max_age: int = Field(2 * 365 * 24 * 60 * 60, description="Max age in seconds for delete operations. Default: 2 years")
    pid_file_name: str = Field("nextcloud_micos_export", description="Name of the pid file.")
    pid_file_path: Path = DirectoryPath("/tmp", description="Path to pid file.", exists=True)
    skip_zeros_on_username: bool = Field(False, description="Skip zeros on username.")
    nextcloud_db_name: str = Field("nextcloud", description="Name of the nextcloud database.")
    nextcloud_db_user: str = Field("lohnexport", description="User of the nextcloud database.")
    nextcloud_db_password: str = Field(..., description="Password of the nextcloud database.")
