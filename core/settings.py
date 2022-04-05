import os
import json


class Settings:
    """This class holds all necessary custom user information."""
    def __init__(self):
        self.cache_file = os.path.dirname(os.path.realpath(__file__)) + "/cache.json"
        self.settings = self.read()

    def write(self):
        """Edit json file."""
        with open(self.cache_file, "w") as outfile:
            json.dump(self.settings, outfile, indent=4)

    def read(self) -> dict:
        """Read json file."""
        with open(self.cache_file) as json_file:
            cache_data = json.load(json_file)
            return cache_data
