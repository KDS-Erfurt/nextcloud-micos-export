from nextcloud_micos_export.Settings import Settings
from pydantic import BaseModel, PrivateAttr

settings = Settings()


class FileNameModel(BaseModel):
    _file_name: str = PrivateAttr()
    Abrechnungskreis: str
    Personalnummer: str

    def __init__(self, file_name: str):
        field_names = list(self.schema()["properties"].keys())

        file_name_backup = file_name
        data = {}
        file_name = file_name[file_name.index("_") + 1:]
        for field_name in field_names:
            value = None
            for separator in ["#", "_", "."]:
                if separator not in file_name:
                    continue
                value = file_name[:file_name.index(separator)]
                file_name = file_name[file_name.index(separator) + 1:]
                break
            if value is None:
                raise ValueError(f"Can't parse '{file_name_backup}'")
            data[field_name] = value

        super().__init__(**data)
        self._file_name = file_name

    def parse_dst_path(self):
        current_dst_path = settings.output_path / f"{self.Abrechnungskreis}{self.Personalnummer}"
        if settings.skip_zeros_on_username:
            if not current_dst_path.is_dir():
                current_dst_path = settings.output_path / f"{self.Abrechnungskreis.lstrip('0')}{self.Personalnummer}"
        current_dst_path /= "files"
        return current_dst_path


class LN028File(FileNameModel):
    Zahldatum: str
    Abrechnungsdatum: str

    def parse_dst_path(self):
        out = FileNameModel.parse_dst_path(self)
        out /= f"VDN_{self.Abrechnungskreis}_{self.Personalnummer}_{self.Zahldatum}_{self.Abrechnungsdatum}.pdf"
        return out


class DUA04File(FileNameModel):
    Zahldatum: str
    Abrechnungsdatum: str
    Ablagedatum: str

    def parse_dst_path(self):
        out = FileNameModel.parse_dst_path(self)
        out /= f"SVB_{self.Abrechnungskreis}_{self.Personalnummer}_{self.Zahldatum}_{self.Abrechnungsdatum}_{self.Ablagedatum}.pdf"
        return out


class LSTBFile(FileNameModel):
    Ordnungsnummer: str
    Jahr: str
    Ablagedatum: str

    def parse_dst_path(self):
        out = FileNameModel.parse_dst_path(self)
        out /= f"LSTB_{self.Abrechnungskreis}_{self.Personalnummer}_{self.Ordnungsnummer}_{self.Jahr}.pdf"
        return out
