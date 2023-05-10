# -*- coding: utf-8 -*-

"""
__author__ = "iEpic"
__email__ = "epicunknown@gmail.com"
"""

import json
from json import JSONDecodeError


default_settings = {
    "allowToResumeDownloads": True,
    "checkForUpdates": True,
    "checkIfFileIsAlreadyDownloaded": True,
    "defaultOutputLocation": False,
    "downloadsDatabaseLocation": "./database.p",
    "episodePadding": 2,
    "includeShowDesc": True,
    "saveDownloadLocation": True,
    "saveFormat": "{show}-S{season}E{episode}-{desc}",
    "seasonPadding": 2,
    "useKnownDownloadLocation": True
}


class Settings:
    """Object that holds user settings"""

    def __init__(self, settings_file):
        self._settings = {}
        self._settings_file = settings_file

        try:
            with open(self._settings_file) as file:
                self._settings = json.load(file)
                print(f"Settings loaded successfuly from {self._settings_file}")
        except FileNotFoundError:
            print(f"Failed to load {self._settings_file}, creating {self._settings_file} with default settings")
            self._settings = default_settings
            self._write_settings_to_file()
        except (JSONDecodeError) as error:
            print(f"Failed to open {self._settings_file} as JSON", str(error))
            raise error

    def _write_settings_to_file(self):
        try:
            with open(self._settings_file, 'w') as file:
                file.write(json.dumps(self._settings, indent=4, sort_keys=True))
            print(f"Settings file {self._settings_file} written successfully")
        except Exception:
            print(f"Failed to open or write file {self._settings_file}")

    def get_setting(self, setting_name):
        """Get the value for a setting"""

        if setting_name in self._settings:
            return self._settings[setting_name]
