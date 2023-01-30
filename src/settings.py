import os
import json


class Settings:
    """This class holds all necessary custom user information."""
    def __init__(self) -> None:
        self.cache_file: str = os.path.dirname(os.path.realpath(__file__)) + "/cache.json"
        self.settings: dict = self.read()

    def write(self) -> None:
        """Edit json file."""
        with open(self.cache_file, "w") as outfile:
            json.dump(self.settings, outfile, indent=4)

    def read(self) -> dict:
        """Read json file."""
        with open(self.cache_file) as json_file:
            cache_data: dict = json.load(json_file)
            return cache_data
