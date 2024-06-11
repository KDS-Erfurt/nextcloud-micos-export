__title__ = "Nextcloud Micos Export"
__name__ = "nextcloud_micos_export"
__description__ = "Move files from input to output folder and delete old files from output folder."
__license__ = "GPL-3.0"
__author__ = "Julius Koenig"
__author_email__ = "julius.koenig@kds-kg.de"
__version__ = "0.5.2"

from nextcloud_micos_export.Settings import Settings
from wiederverwendbar.logger import LoggerSingleton

Settings(file_path="settings",
         init=True)

LoggerSingleton(name=__name__, settings=Settings(), init=True)
