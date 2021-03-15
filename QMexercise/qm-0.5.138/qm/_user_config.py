from os.path import expanduser
import json

home = expanduser("~")


class UserConfig(object):
    def __init__(self, **kwargs):
        super(UserConfig, self).__init__()
        self.manager_port = kwargs.get("quantumMachinesManager_port", 9510)
        self.manager_host = kwargs.get("quantumMachinesManager_host", "localhost")
        self.strict_healthcheck = kwargs.get("quantumMachinesManager_strict_healthcheck", True)


def _load_config_file():
    try:
        with open(home + "/.qm/config.json", "r+") as file:
            return json.load(file)
    except Exception:
        return {}


def load_user_config():
    thejson = _load_config_file()
    return UserConfig(**thejson)
