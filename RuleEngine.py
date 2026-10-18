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

    def __VerifyRule(self, split):
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
            else:
                split = rule["rule"].split(" ")

                # next rule if rule verification fails
                if not self.__VerifyRule(split):
                    print(f"Skipping malformed rule {r} in config.json rules - {rule}")
                    continue

                lhs = split[0]
                op = split[1]
                rhs = split[2]

                if re.match(r"^NULL$", split[0].upper()):
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

    def Run(self, headers):
        confidence: float = 0.0
        reasoning = {}

        # handle any invalid headers first
        # if multiple of the same originator headers, immediately mark as malicious
        for header in headers:
            if confidence >= 1.0:
                confidence = 1.0 # suppress confidence to max 1.0
                return confidence, reasoning 

            if header is None or header == "" or not re.match(r"^[A-Z-]+$", header):
                confidence += 0.2
                reasoning["20000"] = f"Malformed header detected. (+{confidence})"

            if header in ["FROM", "SENDER", "REPLY-TO"] and type(headers[header]) is list and len(headers[header]) > 1:
                confidence = 1.0
                reasoning["20001"] = f"Multiple FROM headers detected. (+{confidence})"

        for rule in self.__ruleDict:
            if confidence >= 1.0:
                confidence = 1.0 # suppress confidence to max 1.0
                return confidence, reasoning

            lhs = self.__ruleDict[rule]["lhs"]
            rhs = self.__ruleDict[rule]["rhs"]
            op = self.__ruleDict[rule]["op"]
            ruleType = self.__ruleDict[rule]["type"]

            # skip processing for all rules if the header is not found at all
            if ruleType == "normal":
                if lhs not in headers.keys() or rhs not in headers.keys():
                    continue
            elif ruleType == "null" and lhs == "":
                if rhs not in headers.keys():
                    continue
            elif ruleType == "null" and rhs == "":
                if lhs not in headers.keys():
                    continue
            else:
                raise RuntimeError("You should never hit this error message!")

        return confidence, reasoning