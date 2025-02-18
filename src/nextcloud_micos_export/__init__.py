__title__ = "Nextcloud Micos Export"
__name__ = "nextcloud-micos-export"
__description__ = "Move files from input to output folder and delete old files from output folder."
__license__ = "GPL-3.0"
__author__ = "Kirchhoff Datensysteme Services GmbH & Co. KG"
__author_email__ = "service@kds-kg.de"
__version__ = "0.5.3"

from nextcloud_micos_export.Settings import Settings
from wiederverwendbar.logger import LoggerSingleton

Settings(file_path="settings",
         init=True)

LoggerSingleton(name=__name__, settings=Settings(), init=True)
