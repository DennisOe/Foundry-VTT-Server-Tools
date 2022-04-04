import json


class Settings:
    """This class holds all necessary custom user information."""
    # Server information
    host = ""
    user = ""
    password = ""
    # Foundry information
    proxy = 0
    data_folder = ""
    vtt_folder = ""
    exclude_folders = []
    # Misc information
    last_backup = ""


class EditSettings:
    @staticmethod
    def write():
        with open("cache.json", "w") as outfile:
            json.dump(cached_settings, outfile, indent=4)
    @staticmethod
    def read():
        with open('cache.json') as json_file:
            data = json.load(json_file)
            print(data)
