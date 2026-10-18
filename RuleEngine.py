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
        split = rule.strip().split(" ")

        # too many variables
        if len(split) != 3:
            return False

        # invalid operands
        if split[1] not in ["==", "<", "<=", ">", ">=", "!="]:
            return False

        # rhs is not a number if using COUNT()
        if re.match(r"COUNT\(.*\)", split[0]) and not re.match(r"\d+", split[2]):
            return False

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
                split = rule["rule"].split(" ")

                tempDict = {
                    "lhs": split[0],
                    "op": split[1],
                    "rhs": split[2],
                    "confidence": rule["confidence"]
                }

                self.__ruleDict[r] = tempDict

    def Run(self, headers):
        pass 
