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

            if "confidence" not in rule.keys() or "rule" not in rule.keys() or "description" not in rule.keys():
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
                    rhs = int(rhs)
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
            if rule["type"] == "normal":
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

            elif rule["type"] == "null":
                if rule["lhs"] == "" and rule["rhs"] not in [h.upper() for h in headers.keys()]:
                    continue
                elif rule["rhs"] == "" and rule["lhs"] not in [h.upper() for h in headers.keys()]:
                    continue

                if rule["lhs"] == "" and self.__Compare("", rule["op"], headers.get_all(rule["rhs"])):
                    confidence += rule["confidence"]
                    reasoning[ruleNum] = f"{rule["description"]} (+{rule["confidence"]})"
                elif rule["rhs"] == "" and self.__Compare(headers.get_all(rule["lhs"]), rule["op"], ""):
                    confidence += rule["confidence"]
                    reasoning[ruleNum] = f"{rule["description"] (+{rule["confidence"]})}" 
            else:
                # this should technically never happen
                raise RuntimeError("Invalid rule supplied.")

        return confidence, reasoning