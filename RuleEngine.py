import os
import json
import re

class RuleEngine:
    def __init__(self):
        self.__overrideFile: str = f"{os.path.dirname(__file__)}/overrides.json"
        self.__overrideList: list[str] = []
        self.__confidence: float = 0.0

        if not os.path.exists(self.__overrideFile):
            raise FileNotFoundError("overrides.json not found.")

        self.__LoadOverrides()

    # confidence getter
    @property
    def confidence(self):
        return self.__confidence

    def __LoadOverrides(self):
        try:
            full_json = json.load(open(self.__overrideFile, "r"))
        except:
            raise RuntimeError("Invalid overrides.json supplied.")

        for override in set(full_json["overrides"]):
            # check if it's a valid email address or domain
            if not re.match(r"(\w+@)?\w+(\.\w+){1,4}", override):
                raise ValueError(f"Invalid domain or email address in overrides - {override}.")

        self.__overrideList = list(set(full_json["overrides"]))

    def Run(self, headers):
        print(f"Running rule engine against {headers}.")
        return 0.0