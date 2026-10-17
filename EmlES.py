from RuleEngine import RuleEngine

import os
import re

class EmlES:
    # init static rule engine
    __ruleEngine = RuleEngine()

    def __init__(self, filePath):
        self.__confidence: float = 0.0 # confidence rating, this will come later
        self.__emlFile: str = "None" # path to .eml file
        self.__headers: dict[str] = {} # eml file headers
        self.__content: str = "None" # eml file content

        # parsing
        self.__ParseEmlHeaders(filePath) # immediately parse the input file

        # run rules
        self.__confidence = self.__ruleEngine.Run(self.__headers)

    def __eq__(self, other):
        if not self.__class__ is other.__class__:
            return NotImplemented
        else:
            return self.__emlFile == other.__emlFile

    # change this to eventually only print what the user wants to see
    def __str__(self):
        return f"""Headers: {self.__headers}
Content: {self.__content}
File Path: {self.__emlFile}
Confidence: {self.__confidence}
"""

    def __HeadersToKV(self, headerString):
        if re.match(r"^[A-Za-z-]+:\s?.*$", headerString):
            parts = headerString.split(":", 1)
            return parts[0], parts[1].strip()
        else:
            raise ValueError

    def __ParseEmlHeaders(self, filePath):
        if filePath.endswith(".eml") and os.path.isfile(filePath):
            ctype = "" # store content type string

            with open(filePath, 'r', errors="ignore") as eml:
                while (True):
                    line = eml.readline()

                    # parse each line until a single \n or a blank line
                    if line == "\n" or line == "":
                        break

                    if line.lower().startswith("content-type") or line.lower().startswith("\t"):
                        ctype += line.strip() # collect all the content-type into a single line
                    else:
                        try:
                            key, value = self.__HeadersToKV(line)
                            self.__headers[key] = value
                        except ValueError:
                            pass

                # read the remaining lines as content
                self.__content = eml.read()

            # parse the content-type
            try:
                key, value = self.__HeadersToKV(ctype)
                self.__headers[key] = value
            except ValueError:
                pass

        else:
            raise RuntimeError("Invalid .eml file supplied.")

        # check if headers are empty
        if len(self.__headers.keys()) == 0:
            raise RuntimeError("Invalid .eml file supplied.")

        # set the file name in the class
        self.__emlFile = filePath
