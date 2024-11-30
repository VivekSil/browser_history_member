import unittest
from src.utils.config_reader import ConfigReader


def test_config_reader():
    config_reader = ConfigReader()
    assert config_reader.get_temp_data_folder() is not None
    assert isinstance(config_reader.get_temp_data_folder(), str)
    assert "tmp" in config_reader.get_temp_data_folder()