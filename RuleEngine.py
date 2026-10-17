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
        self.__LoadRules()

    def __LoadOverrides(self):
        try:
            full_json = json.load(open(self.__ruleFile, "r"))
        except:
            raise RuntimeError("Invalid config.json supplied.")

        for override in set(full_json["overrides"]):
            # check if it's a valid email address or domain
            if not re.match(r"(\w+@)?\w+(\.\w+){1,4}", override):
                print(f"Skipping invalid domain or email address in config.json overrides - {override}.")
            else:
                self.__overrideList += override

    def __VerifyRule(self, rule):
        # write something here to verify the syntax of rules
        return True

    def __LoadRules(self):
        try:
            full_json = json.load(open(self.__ruleFile, "r"))
        except:
            raise RuntimeError("Invalid config.json supplied.")

        for r in full_json["rules"]:
            rule = full_json["rules"][r]

            if "confidence" not in rule.keys() or "rule" not in rule.keys():
                print(f"Skipping rule {r} with invalid properties in config.json rules - {rule}")
            elif not self.__VerifyRule(rule["rule"]):
                print(f"Skipping malformed rule {r} in config.json rules - {rule}")
            else:
                self.__ruleDict[r] = rule

    def Run(self, headers):
        new_dict = {"test": 0.1}
        return 0.1, new_dict