import configparser
from pathlib import Path


class ConfigReader:
    _instance = None
    _config = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ConfigReader, cls).__new__(cls, *args, **kwargs)
            cls._config = configparser.ConfigParser()
            config_path = Path(__file__).parent.parent.parent / "config" / "config.ini"
            cls._config.read(config_path)
        return cls._instance

    def get_temp_data_folder(self) -> str:
        temp_data_folder = self._config["DEFAULT"]["temp_data_folder"]
        temp_data_folder_path = Path(temp_data_folder).expanduser()

        # Creare la cartella se non esiste
        if not temp_data_folder_path.exists():
            temp_data_folder_path.mkdir(parents=True, exist_ok=True)

        return str(temp_data_folder_path)

    def get_api_name(self) -> str:
        return self._config["API_INFO"]["API_NAME"]

    def get_aggregator_datasite(self) -> str:
        return self._config["API_INFO"]["AGGREGATOR_DATASITE"]

    def get_interval(self) -> int:
        return int(self._config["API_INFO"]["INTERVAL"])

    def get_allow_top(self) -> bool:
        return self._config["API_INFO"].getboolean("ALLOW_TOP")