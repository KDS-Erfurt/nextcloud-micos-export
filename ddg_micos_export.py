#!/usr/bin/python3

import os
import logging
import shutil
import sys
import time
from enum import Enum
from logging.handlers import RotatingFileHandler
from pathlib import Path

import psutil as psutil
from pydantic import BaseModel

settings_filepath = Path("settings.json")


class LogLevels(str, Enum):
    debug = 'DEBUG'
    info = 'INFO'
    warning = 'WARNING'
    error = 'ERROR'


class Settings(BaseModel):
    dry_run: bool = False
    input_path: Path
    output_path: Path
    on_fail_path: Path
    log_filepath: Path
    log_level: LogLevels = LogLevels.warning
    log_file_maxsize: int = 10737418240  # 10MB
    log_file_max_count: int = 5
    loop_delay: float = 2

    class Config:
        use_enum_values = True


class FileModel(BaseModel):
    Listennummer: str
    Abrechnungskreises: str
    Personalnummer: str
    Zahldatum: str
    Abrechnungsdatum: str


def is_running(script):
    for q in psutil.process_iter():
        if q.name().startswith('python'):
            cmdline = q.cmdline()
            for cmdline_arg in cmdline:
                if script in cmdline_arg:
                    if q.pid != os.getpid():
                        return True
    return False


def on_fail(src_path: Path):
    log.info(f"Move '{src_path}' to '{settings.on_fail_path / src_path.name}'")
    if not settings.dry_run:
        try:
            shutil.move(current_src_path, settings.on_fail_path / src_path.name)
        except Exception as e:
            log.error(f"Cant move file. {e}")


if __name__ == '__main__':
    file = Path(__file__).name
    if is_running(file):
        print(f"Script '{file}' is already running.")
        sys.exit(1)

    if not settings_filepath.is_file():
        print(f"Settings file '{settings_filepath}' not found.")
        sys.exit(1)

    settings = Settings.parse_file(settings_filepath)
    logging.basicConfig(level=settings.log_level)
    log = logging.getLogger()
    handler = RotatingFileHandler(settings.log_filepath, maxBytes=settings.log_file_maxsize, backupCount=settings.log_file_max_count - 1)
    handler.setFormatter(logging.Formatter("[%(levelname)s]\t- %(asctime)s: %(message)s"))
    log.addHandler(handler)
    log.info(f"Setting: {settings}")

    if settings.dry_run:
        log.warning(f"--- DRY RUN ---")

    last_run = 0
    while True:
        if last_run + settings.loop_delay > time.time():
            time.sleep(0.001)
            continue
        log.info(f"--- Start loop ---")
        last_run = time.time()
        if not settings.input_path.is_dir():
            log.error(f"Input path '{settings.input_path}' not found.")
            continue

        if not settings.output_path.is_dir():
            log.error(f"Output path '{settings.input_path}' not found.")
            continue

        if not settings.on_fail_path.is_dir():
            log.error(f"On fail path '{settings.on_fail_path}' not found.")
            continue

        field_names = list(FileModel.schema()["properties"].keys())

        for root_path, dirs, files in os.walk(settings.input_path):
            for file_path in files:
                field_next = 0
                work_file_path = file_path

                log.info(f"Current file: {work_file_path}")

                file_model_dict = {}
                while "_" in work_file_path:
                    file_model_dict[field_names[field_next]] = work_file_path[:work_file_path.index("_")]
                    work_file_path = work_file_path[work_file_path.index("_") + 1:]
                    field_next += 1

                file_model = FileModel(**file_model_dict)
                log.info(f"Current file(parsed): {file_model}")

                current_src_path = settings.input_path / file_path
                current_dst_path = settings.output_path / f"{file_model.Abrechnungskreises}{file_model.Personalnummer}"

                if not current_dst_path.exists():
                    log.error(f"Destination path '{current_dst_path}' not found.")
                    on_fail(current_src_path)
                    continue

                if not current_dst_path.is_dir():
                    log.error(f"Destination path '{current_dst_path}' is not a directory.")
                    on_fail(current_src_path)
                    continue

                log.info(f"Current file(target_path): {current_dst_path}")
                log.info(f"Move '{current_src_path}' to '{current_dst_path}'")
                if not settings.dry_run:
                    try:
                        current_dst_path /= "files"
                        if not current_dst_path.is_dir():
                            log.info(f"MKDIR '{current_dst_path}'")
                            os.mkdir(current_dst_path)
                        shutil.move(current_src_path, current_dst_path)
                    except Exception as e:
                        log.error(f"Cant move file. {e}")
                        on_fail(current_src_path)
                        continue

        log.info(f"--- End loop, sleep for {settings.loop_delay} seconds ---")
