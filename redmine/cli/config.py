import configparser
import os

import click


class Config:
    def __init__(self, *args, **kwargs):
        HOME = os.getenv("HOME")
        self.paths = [
            os.path.join(HOME, ".redmine.conf"),
            os.path.join(HOME, ".redmine/redmine.conf"),
            os.path.join(HOME, ".config/redmine/redmine.conf")
        ]
        self.url = None
        self.api_key = None
        self.me = None
        self.aliases = {}
        self.read()

    def read(self):
        config = configparser.ConfigParser()

        for path in self.paths:
            if os.path.isfile(path):
                config.read(path)
                break

        self.url = config["redmine"]["url"]
        self.api_key = config["redmine"]["key"]

        if "me" in config["redmine"]:
            self.me = config["redmine"]["me"]

        try:
            self.aliases.update(config.items("aliases"))
        except configparser.NoSectionError:
            pass

        return config


pass_config = click.make_pass_decorator(Config, ensure=True)
