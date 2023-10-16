from controllogger.logger.control import ControlLogger
from controllogger.misc.easy_logger_config import EasyLoggerConfig
from controllogger.misc.output_logger_config import OutputLoggerConfig

from .Settings import Settings, settings
from .FileNameModels import FileNameModel, LN028File, DUA04File, LSTBFile

__title__ = "Nextcloud Micos Export"
__description__ = "Move files from input to output folder and delete old files from output folder."
__author__ = "Julius König"
__version__ = "0.4.2"

control_logger = ControlLogger(EasyLoggerConfig(name="nextcloudmicosexport",
                                                level=settings.log_level,
                                                output_loggers=[
                                                    OutputLoggerConfig(name="console", console=True),
                                                    OutputLoggerConfig(name="file",
                                                                       file=True,
                                                                       file_path=settings.log_filepath / "nextcloudmicosexport.log",
                                                                       file_max_size=settings.log_file_maxsize,
                                                                       file_backup_count=settings.log_file_max_count)
                                                ]))
