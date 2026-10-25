from classes.RuleEngine import RuleEngine

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

    def __str__(self):
        if len(self.__reasoning) > 0:
            outputReasoning = []

            for rule in self.__reasoning:
                outputReasoning.append(f"Rule {rule}: {self.__reasoning[rule]}")

            outputReasoning = "\n\t".join(outputReasoning)
        else:
            outputReasoning = "None"

        match self.__confidence:
            case self.__confidence if 0.0 <= self.__confidence < 0.2:
                outputConfidence = f"Extremely unlikely to be a malicious or spam email. (Confidence score: {self.__confidence})"
            case self.__confidence if 0.2 <= self.__confidence < 0.4:
                outputConfidence = f"Very unlikely to be a malicious or spam email. (Confidence score: {self.__confidence})"
            case self.__confidence if 0.4 <= self.__confidence < 0.6:
                outputConfidence = f"Likely to be a malicious or spam email. (Confidence score: {self.__confidence})"
            case self.__confidence if 0.6 <= self.__confidence < 0.8: 
                outputConfidence = f"Very likely to be a malicious or spam email. (Confidence score: {self.__confidence})"
            case self.__confidence if 0.8 <= self.__confidence <= 1.0:
                outputConfidence = f"Extremely likely to be a malicious or spam email. (Confidence score: {self.__confidence})"
            case _:
                # this likely wouldn't happen at all
                raise ValueError(f"Invalid confidence value of {self.__confidence}")

        return f"Successfully processed: {self.__emlFile}\nOutcome: {outputConfidence}\nRules Triggered:\n\t{outputReasoning}"

    def __ParseEmlHeaders(self, filePath):
        if not os.path.exists(filePath):
            raise ValueError(f"Invalid file provided.")

        self.__emlFile = filePath

        parser = BytesFeedParser(policy=policy.default)

        with open(filePath, 'rb') as emlFile:
            for line in emlFile:
                parser.feed(line)

        self.__headers = parser.close()

        if len(self.__headers.keys()) == 0:
            raise RuntimeError(f"Unable to parse input .eml file due to malformed headers.")

        emailRegex = re.compile(r"[A-Za-z0-9-_.]+@[A-Za-z0-9-]+\.(?:\.?[A-Za-z0-9-]+){1,}")

        if len(self.__headers.defects) > 0:
            self.__confidence += len(self.__headers.defects) * 0.2

            if len(self.__headers.defects) == 1:
                string = "malformed header"
            else:
                string = "malformed headers"

            self.__reasoning["1000"] = f"{len(self.__headers.defects)} {string} detected. (+{self.__confidence})"

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
                        if email == "" or email == None:
                            email = "None"

                        self.__confidence += 0.4

                        if not "1001" in self.__reasoning.keys():
                            self.__reasoning["1001"] = []

                        self.__reasoning["1001"].append(f"Invalid email address of {email} in the {header} header. (+0.4)")

                        if self.__confidence >= 1.0:
                            self.__confidence = 1.0
                            break