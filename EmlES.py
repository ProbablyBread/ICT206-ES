from RuleEngine import RuleEngine

import os
import re

class EmlES:
    # init static rule engine
    __ruleEngine = RuleEngine()

    def __init__(self, filePath):
        self.__confidence: float = 0.0 # confidence rating
        self.__reasoning: dict[str] = {} # dict of rule hits 
        self.__emlFile: str = "None" # path to .eml file
        self.__headers: dict[str] = {} # eml file headers

        # parse the input file
        self.__ParseEmlHeaders(filePath)

        # run rules
        self.__confidence, self.__reasoning = self.__ruleEngine.Run(self.__headers)

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
        if not os.path.exists(filePath) or not filePath.endswith(".eml"):
            raise ValueError(f"Invalid file provided.")

        with open(filePath, 'rb') as emlFile:
            lines = []

            while True:
                line = emlFile.readline().decode()

                # read only the headers
                if line == "\n" or line == "\r\n" or line == "":
                    break

                lines.append(line)

        self.__emlFile = filePath
        key = None
        value = None

        for line in lines:
            if not re.match(r"^\s+.*$", line):
                split = line.strip().split(":", 1) # split only once
            else:
                split = []

            if len(split) > 1:
                key = split[0].upper()
                value = split[1]

                if key not in self.__headers.keys():
                    self.__headers[key] = value.strip()
                else:
                    if type(self.__headers[key]) is not list:
                        self.__headers[key] = [self.__headers[key]]

                    self.__headers[key].append(value.strip())
            else:
                # detect unix mbox from header as the first line
                if key is None and re.match(r"^From\s.*$", split[0]):
                    pass # ignore and do not add
                else:
                    self.__headers[key] += f" {line.strip()}" # reuse the previous key since it wasn't updated

        if len (self.__headers.keys()) == 0:
            raise ValueError(f"Unable to parse input .eml file due to invalid headers.")