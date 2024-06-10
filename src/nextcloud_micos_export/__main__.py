import datetime
import os
import shutil
import sys
import time
from pathlib import Path

import pid
from nextcloud_micos_export import Settings
from nextcloud_micos_export.FileNameModels import LN028File, DUA04File, LSTBFile
from wiederverwendbar.logger import LoggerSingleton

logger = LoggerSingleton()
settings = Settings()


def move_but_rename_exist(src_path: Path, dst_path: Path):
    count = None
    while True:
        out_path = dst_path if count is None else dst_path.parent / dst_path.name / f".{count}"
        if out_path.exists():
            continue
        if settings.dry_run:
            logger.warning(f"Move(--- DRY RUN ---) '{src_path}' to '{out_path}'")
            time.sleep(1)
        else:
            logger.info(f"Move '{src_path}' to '{out_path}'")
            try:
                shutil.move(src_path, out_path)
            except Exception as e:
                logger.error(f"Cant move file. {e}")
                raise e
        break


def move():
    logger.debug(f"--- move ---")
    input_path_listdir = os.listdir(settings.input_path)
    for file_name in input_path_listdir:
        current_src_path = settings.input_path / file_name
        if not current_src_path.is_file():
            continue
        try:
            try:
                if "LN028" in file_name:
                    file_model = LN028File(file_name)
                elif "DUA04" in file_name:
                    file_model = DUA04File(file_name)
                elif "LSTB" in file_name:
                    file_model = LSTBFile(file_name)
                else:
                    logger.error(f"Unknown Filetype '{current_src_path}'.")
                    continue
            except ValueError as _e:
                logger.error(_e)
                continue

            logger.info(f"Current file: {current_src_path}")
            logger.info(f"Current file(parsed): {file_model}")

            current_dst_path = file_model.parse_dst_path()
            logger.info(f"Current file(target_path): {current_dst_path}")

            postfix = 2
            renamed = False
            try_path = current_dst_path
            while try_path.exists():
                try_path = current_dst_path.parent / (current_dst_path.name[:current_dst_path.name.index(
                    ".")] + f"_{postfix}" + current_dst_path.suffix)
                renamed = True
                postfix += 1
            if renamed:
                logger.info(f"Renamed file: {current_dst_path} -> {try_path}")
                current_dst_path = try_path

            if not current_dst_path.parent.parent.is_dir():
                raise RuntimeError(f"Destination path '{current_dst_path.parent.parent}' not found.")

            logger.info(f"Move '{current_src_path}' to '{current_dst_path}'")
            if settings.dry_run:
                logger.warning(f"Move(--- DRY RUN ---) '{current_src_path}' to '{current_dst_path}'")
                continue
            if not current_dst_path.parent.is_dir():
                logger.info(f"MKDIR '{current_dst_path.parent}'")
                os.mkdir(current_dst_path.parent)
            shutil.move(current_src_path, current_dst_path)
            ts = datetime.datetime.now().timestamp()
            os.utime(current_dst_path, (ts, ts))
        except Exception as e:
            logger.error(e)
            move_but_rename_exist(current_src_path, settings.on_fail_path / current_src_path.name)

    logger.debug(f"--- End move ---")


def delete():
    logger.debug(f"--- delete ---")
    check_files = []
    for c_dir in settings.output_path.iterdir():
        if not c_dir.is_dir():
            continue
        # check if dir name has 10 chars
        if len(c_dir.name) != 10:
            continue
        # check if dir name is digit
        try:
            int(c_dir.name)
        except ValueError:
            continue

        if (c_dir / "files").is_dir():
            for c_file in (c_dir / "files").iterdir():
                if c_file.is_file():
                    check_files.append(c_file)

    # check if older than delete_max_age
    for file in check_files:
        if not os.path.isfile(file):
            continue
        if not os.path.getmtime(file) < time.time() - settings.delete_max_age:
            continue
        if settings.dry_run:
            logger.warning(f"Move old file (--- DRY RUN ---) '{file}' to '{settings.on_delete_path / file.name}'")
            time.sleep(1)
        else:
            logger.info(f"Move old file '{file}' to '{settings.on_delete_path / file.name}'")
            move_but_rename_exist(file, settings.on_delete_path / file.name)
        continue
    logger.debug(f"--- End delete ---")


if __name__ == '__main__':
    # cwd = Path(__file__).parent
    # os.chdir(cwd)
    # file = Path(__file__).name

    try:
        with pid.PidFile(pidname=settings.pid_file_name, piddir=settings.pid_file_path):
            try:
                if settings.dry_run:
                    logger.warning(f"--- DRY RUN ---")

                if settings.log_file_path is not None:
                    if not settings.log_file_path.parent.is_dir():
                        logger.error(f"Input path '{settings.log_file_path.parent}' not found.")
                        sys.exit(1)
                if not settings.input_path.is_dir():
                    logger.error(f"Input path '{settings.input_path}' not found.")
                    sys.exit(1)
                if not settings.output_path.is_dir():
                    logger.error(f"Output path '{settings.input_path}' not found.")
                    sys.exit(1)
                if not settings.on_fail_path.is_dir():
                    logger.error(f"On fail path '{settings.on_fail_path}' not found.")
                    sys.exit(1)
                if not settings.on_delete_path.is_dir():
                    logger.error(f"On delete path '{settings.on_delete_path}' not found.")
                    sys.exit(1)

                last_move = 0
                last_delete = 0
                while True:  # main loop
                    try:
                        if last_move + settings.move_interval <= time.time():
                            last_move = time.time()
                            move()
                        elif last_delete + settings.delete_interval <= time.time():
                            last_delete = time.time()
                            delete()
                        else:
                            time.sleep(0.001)
                            continue
                    except Exception as e:
                        logger.error(e)
                        time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Nextcloud Micos Export stopped by user.")
                sys.exit(0)
    except pid.base.PidFileAlreadyLockedError:
        logger.error(f"Already running. Pid file '{settings.pip_file}' exists.")
        sys.exit(1)
