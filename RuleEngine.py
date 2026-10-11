import os

class RuleEngine:
    def __init__(self):
        self.__ruleFile: str = f"{os.path.dirname(__file__)}/config.ini"
        self.__ruleDict: dict[str] = {}
        self.__ruleOverrides: dict[str] = {}

        if not os.path.exists(self.__ruleFile):
            raise FileNotFoundError("config.ini not found.")

        if not self.__VerifyRules():
            raise SyntaxError("Invalid config.ini supplied.")

        self.__ParseRules()

    def __VerifyRules(self):
        pass

    def __ParseRules(self):
        pass