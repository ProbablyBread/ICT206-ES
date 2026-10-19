import os
import json
import re

from email.message import EmailMessage

class RuleEngine:
    __ORIGINATOR_HEADERS = ["FROM", "REPLY-TO", "SENDER"]
    __DESTINATION_HEADERS = ["TO", "CC", "BCC"]

    def __init__(self):
        self.__ruleFile: str = f"{os.path.dirname(__file__)}/config.json"
        self.__ruleDict: dict[str] = {}
        self.__senderOverrideDomains: list[str] = []
        self.__senderOverrideEmails: list[str] = []
        self.__destinationOverrideDomains: list[str] = []
        self.__destinationOverrideEmails: list[str] = []

        if not os.path.exists(self.__ruleFile):
            raise FileNotFoundError("config.json not found.")

        self.__LoadOverrides()
        self.__LoadRules()

        print(self.__ruleDict)

    def __LoadOverrides(self):
        try:
            full_json = json.load(open(self.__ruleFile, "r"))
        except:
            raise RuntimeError("Invalid config.json supplied.")

        # load sender overrides
        for override in set(full_json["senderOverrides"]):
            if re.match(r"^\w+@\w+(\.\w+){1,}$", override):
                self.__senderOverrideEmails.append(override)
            elif re.match(r"^\w+(\.\w+){1,}$", override):
                self.__senderOverrideDomains.append(override)
            else:
                print(f"Skipping invalid email/domain of {override} in senderOverrides in config.json.")

        # load destination overrides
        for override in set(full_json["destinationOverrides"]):
            if re.match(r"^\w+@\w+(\.\w+){1,}$", override):
                self.__destinationOverrideEmails.append(override)
            elif re.match(r"^\w+(\.\w+){1,}$", override):
                self.__destinationOverrideDomains.append(override)
            else:
                print(f"Skipping invalid email/domain of {override} in senderOverrides in config.json.")

        # deduplicate all lists
        self.__senderOverrideEmails = list(set(self.__senderOverrideEmails))
        self.__senderOverrideDomains = list(set(self.__senderOverrideDomains))
        self.__destinationOverrideEmails = list(set(self.__destinationOverrideEmails))
        self.__destinationOverrideDomains = list(set(self.__destinationOverrideDomains))

    def __VerifyRule(self, split):
        # too many variables
        if len(split) != 3:
            return False

        # invalid operands
        if split[1] not in ["==", "<", "<=", ">", ">=", "!="]:
            return False

        # invalid count rule type
        if re.match(r"^COUNT\(.*\)", split[0]) and not re.match(r"\d+", split[2]):
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
            else:
                split = rule["rule"].split(" ")

                # next rule if rule verification fails
                if not self.__VerifyRule(split):
                    print(f"Skipping malformed rule {r} in config.json rules - {rule}")
                    continue

                lhs = split[0]
                op = split[1]
                rhs = split[2]

                if re.match(r"^COUNT\(.*\)", split[0].upper()):
                    matchObj = re.findall(r"^COUNT\((\w+)\)", split[0].upper())
                    ruleType = "count"
                    lhs = matchObj[0]
                elif re.match(r"^NULL$", split[0].upper()):
                    ruleType = "null"
                    lhs = ""
                elif re.match(r"^NULL$", split[2].upper()):
                    ruleType = "null"
                    rhs = ""
                else:
                    ruleType = "normal"

                tempDict = {
                    "lhs": lhs, 
                    "op": op,
                    "rhs": rhs,
                    "confidence": rule["confidence"],
                    "type": ruleType
                }

                self.__ruleDict[r] = tempDict

    def __CmpEquals(self, lhs, rhs):
        return lhs == rhs

    def __CmpLessThan(self, lhs, rhs):
        return lhs < rhs

    def __CmpLessEquals(self, lhs, rhs):
        return lhs <= rhs

    def __CmpMoreThan(self, lhs, rhs):
        return lhs > rhs

    def __CmpMoreEquals(self, lhs, rhs):
        return lhs >= rhs

    def __CmpNotEquals(self, lhs, rhs):
        return lhs != rhs

    def Run(self, headers: EmailMessage):
        confidence = 0.0
        reasoning = {}

        if headers.defects > 0:
            confidence += len(headers.defects) * 0.2

        return confidence, reasoning