from RuleEngine import RuleEngine

from email.parser import BytesFeedParser
from email.message import EmailMessage
from email import policy

import os

class EmlES:
    # init static rule engine
    __ruleEngine = RuleEngine()

    def __init__(self, filePath):
        self.__confidence: float = 0.0 # confidence rating
        self.__reasoning: dict[str] = {} # dict of rule hits 
        self.__emlFile: str = "None" # path to .eml file
        self.__headers: EmailMessage = None # eml file headers

        # parse the input file
        self.__ParseEmlHeaders(filePath)

        # run rules
        self.__confidence, self.__reasoning = self.__ruleEngine.Process(self.__headers)

    @property
    def confidence(self):
        return self.__confidence

    @property
    def reasoning(self):
        return self.__reasoning

    @property
    def headers(self):
        return self.__headers

    @property
    def emlFile(self):
        return self.__emlFile

    def __eq__(self, other):
        if not self.__class__ is other.__class__:
            return NotImplemented
        else:
            return self.__emlFile == other.__emlFile

    # change this to eventually only print what the user wants to see
    def __str__(self):
        return f"""Headers:\n {self.__headers}\n
File Path: {self.__emlFile}
Confidence: {self.__confidence}
Reasoning: {self.__reasoning}
"""

    def __ParseEmlHeaders(self, filePath):
        if not os.path.exists(filePath):
            raise ValueError(f"Invalid file provided.")

        parser = BytesFeedParser(policy=policy.default)

        with open(filePath, 'rb') as emlFile:
            for line in emlFile:
                parser.feed(line)

        self.__headers = parser.close()

        if len(self.__headers.keys()) == 0:
            raise RuntimeError(f"Unable to parse input .eml file due to malformed headers.")
            
        # TODO: check if originator or destination headers here are encoded
        # TODO: if they are, decode them appropriately before proceeding