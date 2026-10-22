from RuleEngine import RuleEngine

from email.parser import BytesFeedParser
from email.message import EmailMessage
from email import policy

import os
import re

class EmlES:
    __ORIGINATOR_HEADERS = ["FROM", "REPLY-TO", "SENDER"]
    __DESTINATION_HEADERS = ["TO", "CC", "BCC"]

    # init static rule engine
    __ruleEngine = RuleEngine()

    def __init__(self, filePath):
        self.__confidence: float = 0.0 # confidence rating
        self.__reasoning: dict[any][str] = {} # dict of rule hits 
        self.__emlFile: str = "None" # path to .eml file
        self.__headers: EmailMessage = None # eml file headers

        # parse the input file
        self.__ParseEmlHeaders(filePath)

        # run rules if not already fully confident
        if not self.__confidence >= 1.0:
            self.__confidence, self.__reasoning = self.__ruleEngine.Process(self.__headers, self.__confidence, self.__reasoning)

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
        if not type(self) is type(other):
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

        emailRegex = re.compile(r"[A-Za-z0-9-_.]+@[A-Za-z0-9-]+\.(?:\.?[A-Za-z0-9-]+){1,}")

        if len(self.__headers.defects) > 0:
            confidence += len(self.__headers.defects) * 0.2

        for header in self.__ORIGINATOR_HEADERS + self.__DESTINATION_HEADERS:
            emails = self.__headers.get_all(header)

            # extract email address only if header exists
            if emails is not None:
                for email in emails:
                    matches = emailRegex.findall(email)

                    if len(matches) > 0:
                        self.__headers.replace_header(header, matches)
                    else:
                        # if any address in the list cannot be parsed for any reason
                        self.__confidence += 0.8
                        self.__reasoning["0"] = f"Detected invalid email address of {email} in the {header} header."

                        if self.__confidence >= 1.0:
                            self.__confidence = 1.0
                            break