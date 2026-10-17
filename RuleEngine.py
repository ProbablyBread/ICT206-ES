import os
import json
import re

class RuleEngine:
    def __init__(self):
        self.__ruleFile: str = f"{os.path.dirname(__file__)}/config.json"
        self.__ruleDict: dict[str] = {}
        self.__overrideList: list[str] = []

        if not os.path.exists(self.__ruleFile):
            raise FileNotFoundError("config.json not found.")

        self.__LoadOverrides()

    def __LoadOverrides(self):
        try:
            full_json = json.load(open(self.__ruleFile, "r"))
        except:
            raise RuntimeError("Invalid config.json supplied.")

        for override in set(full_json["overrides"]):
            # check if it's a valid email address or domain
            if not re.match(r"(\w+@)?\w+(\.\w+){1,4}", override):
                raise ValueError(f"Invalid domain or email address in config.json overrides - {override}.")

        self.__overrideList = list(set(full_json["overrides"]))

    def Run(self, headers):
        new_dict = {"test": 0.1}
        return 0.1, new_dict