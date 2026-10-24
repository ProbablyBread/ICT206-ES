import os
import json
import re

from email.message import EmailMessage

class RuleEngine:
    def __init__(self):
        self.__ruleFile: str = f"{os.path.dirname(__file__)}/config.json"
        self.__ruleDict: dict[any][str] = {}

        if not os.path.exists(self.__ruleFile):
            raise FileNotFoundError("config.json not found.")

        self.__LoadRules()

    def __VerifyRule(self, split, ruleType):
        # null rule type has too many variables
        if ruleType == "null" and len(split) != 1:
            return False
        # otherwise, it must be 3 variables
        elif len(split) != 3:
            return False

        # check for valid ruleTypes
        if ruleType not in ["address", "regex", "count", "header", "null"]:
            return False

        # invalid operands
        if split[1] not in ["==", "<", "<=", ">", ">=", "!="]:
            return False

        # invalid count rule type
        if ruleType == "count" and not re.match(r"\d+", split[2]):
            return False

        # invalid email address for email rule type
        if ruleType == "address": 
            if not re.match(r"[A-Za-z0-9-_.]+@[A-Za-z0-9-]+\.(?:\.?[A-Za-z0-9-]+){1,}", split[2]):
                return False
            elif split[1] not in ["==", "!="]:
                return False

        # unable to compile regex for regex rule type
        if ruleType == "regex":
            try: 
                _ = re.compile(rf"{split[2]}")
            except:
                return False

            if split[1] not in ["==", "!="]:
                return False

        return True

    def __LoadRules(self):
        try:
            full_json = json.load(open(self.__ruleFile, "r"))
        except:
            raise RuntimeError("Invalid config.json supplied.")

        for r in full_json["rules"]:
            rule = full_json["rules"][r]

            if "confidence" not in rule.keys() or "rule" not in rule.keys() or "description" not in rule.keys() or "ruleType" not in rule.keys():
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
                ruleType = rule["ruleType"]

                # special conditions for specific ruleTypes
                if ruleType == "count":
                    rhs = int(rhs) # cast to int
                elif ruleType == "regex":
                    rhs = re.compile(rf"{rhs}")
                elif ruleType == "null":
                    lhs = split[0]
                    op = "=="
                    rhs = ""

                tempDict = {
                    "lhs": lhs, 
                    "op": op,
                    "rhs": rhs,
                    "confidence": rule["confidence"],
                    "type": ruleType,
                    "description": rule["description"]
                }

                self.__ruleDict[r] = tempDict

    def __Compare(self, lhs, op, rhs):
        match op:
            case "==": return lhs == rhs
            case "<": return lhs < rhs
            case "<=": return lhs <= rhs
            case ">": return lhs > rhs
            case ">=": return lhs >= rhs
            case "!=": return lhs != rhs
            case _: raise ValueError("Invalid comparison operator") # this should technically never happen

    def Process(self, headers: EmailMessage, confidence: float, reasoning: dict[any][str]):
        for rule in self.__ruleDict:
            if confidence >= 1.0:
                confidence = 1.0
                break

            ruleNum = rule
            rule = self.__ruleDict[rule]

            # check each rule type, if headers are missing, skip the rule
            # perform comparison against the actual header value for each rule
            if rule["type"] == "header":
                if rule["lhs"] not in [h.upper() for h in headers.keys()] or rule["rhs"] not in [h.upper() for h in headers.keys()]:
                    continue

                if self.__Compare(headers.get_all(rule["lhs"]), rule["op"], headers.get_all(rule["rhs"])):
                    confidence += rule["confidence"]
                    reasoning[ruleNum] = f"{rule["description"]} (+{rule["confidence"]})"

            elif rule["type"] == "count":
                if rule["lhs"] not in [h.upper() for h in headers.keys()]:
                    continue

                if self.__Compare(len(headers.get_all(rule["lhs"])), rule["op"], rule["rhs"]):
                    confidence += rule["confidence"]
                    reasoning[ruleNum] = f"{rule["description"]} (+{rule["confidence"]})"

            elif rule["type"] == "regex":
                if rule["lhs"] not in [h.upper() for h in headers.keys()]:
                    continue

                if rule["op"] == "==" and rule["rhs"].match(rule["lhs"]):
                    confidence += rule["confidence"]
                    reasoning[ruleNum] = f"{rule["description"]} (+{rule["confidence"]})"
                elif rule["op"] == "!=" and not rule["rhs"].match(rule["lhs"]):
                    confidence += rule["confidence"]
                    reasoning[ruleNum] = f"{rule["description"]} (+{rule["confidence"]})"

            elif rule["type"] == "address" or rule["type"] == "null":
                if rule["lhs"] not in [h.upper() for h in headers.keys()]:
                    continue

                if self.__Compare(rule["lhs"], rule["op"], rule["rhs"]):
                    confidence += rule["confidence"]
                    reasoning[ruleNum] = f"{rule["description"]} (+{rule["confidence"]})"

            else:
                # this should technically never happen
                raise RuntimeError("Invalid rule supplied.")

        return confidence, reasoning