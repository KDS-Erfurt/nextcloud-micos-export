#!/usr/bin/python3

import os
import logging
import shutil
import sys
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path

import pid
from pid import PidFile

from FileNameModels import LN028File, DUA04File, LSTBFile
from Settings import Settings

if __name__ == '__main__':
    cwd = Path(__file__).parent
    os.chdir(cwd)
    file = Path(__file__).name

    settings = Settings()

    try:
        with PidFile(pidname=str(settings.pip_file)):
            logging.basicConfig(level=settings.log_level)
            log = logging.getLogger()
            handler = RotatingFileHandler(settings.log_filepath, maxBytes=settings.log_file_maxsize, backupCount=settings.log_file_max_count - 1)
            handler.setFormatter(logging.Formatter("[%(levelname)s]\t- %(asctime)s: %(message)s"))
            log.addHandler(handler)

            log.info(f"--- STARTUP ---")
            log.info(f"Setting: {settings}")

            if settings.dry_run:
                log.warning(f"--- DRY RUN ---")

            last_run = 0
            while True:  # main loop
                if last_run + settings.loop_delay > time.time():
                    time.sleep(0.001)
                    continue
                log.debug(f"--- Start loop ---")
                last_run = time.time()
                while True:  # only runs ones, continue on dry run or exception
                    try:
                        if not settings.input_path.is_dir():
                            log.error(f"Input path '{settings.input_path}' not found.")
                            sys.exit(1)

                        if not settings.output_path.is_dir():
                            log.error(f"Output path '{settings.input_path}' not found.")
                            sys.exit(1)

                        if not settings.on_fail_path.is_dir():
                            log.error(f"On fail path '{settings.on_fail_path}' not found.")
                            sys.exit(1)

                        input_path_listdir = os.listdir(settings.input_path)
                        for file_name in input_path_listdir:
                            current_src_path = settings.input_path / file_name
                            if not current_src_path.is_file():
                                continue

                            try:
                                if "LN028" in file_name:
                                    file_model = LN028File(file_name)
                                elif "DUA04" in file_name:
                                    file_model = DUA04File(file_name)
                                elif "LSTB" in file_name:
                                    file_model = LSTBFile(file_name)
                                else:
                                    log.error(f"Unknown Filetype '{current_src_path}'.")
                                    continue
                            except ValueError as e:
                                log.error(e)
                                continue

                            log.info(f"Current file: {current_src_path}")
                            log.info(f"Current file(parsed): {file_model}")

                            current_dst_path = file_model.parse_dst_path()
                            log.info(f"Current file(target_path): {current_dst_path}")

                            if current_dst_path.exists():
                                log.warning(f"Destination file already exist '{current_dst_path}' -> delete source.")
                                os.remove(current_src_path)
                                continue

                            if not current_dst_path.parent.parent.is_dir():
                                raise RuntimeError(f"Destination path '{current_dst_path.parent.parent}' not found.")

                            log.info(f"Move '{current_src_path}' to '{current_dst_path}'")
                            if settings.dry_run:
                                log.warning(f"Move(--- DRY RUN ---) '{current_src_path}' to '{current_dst_path}'")
                                continue
                            if not current_dst_path.parent.is_dir():
                                log.info(f"MKDIR '{current_dst_path.parent}'")
                                os.mkdir(current_dst_path.parent)
                            shutil.move(current_src_path, current_dst_path)
                    except Exception as e:
                        log.error(e)
                        if settings.dry_run:
                            log.warning(f"Move(--- DRY RUN ---) '{current_src_path}' to '{settings.on_fail_path / current_src_path.name}'")
                        else:
                            log.info(f"Move '{current_src_path}' to '{settings.on_fail_path / current_src_path.name}'")
                            try:
                                shutil.move(current_src_path, settings.on_fail_path / current_src_path.name)
                            except Exception as e:
                                log.error(f"Cant move file. {e}")
                        continue
                    break
                log.debug(f"--- End loop, sleep for {settings.loop_delay} seconds ---")
    except pid.base.PidFileAlreadyLockedError:
        print(f"Script '{file}' is already running.")
        sys.exit(1)
