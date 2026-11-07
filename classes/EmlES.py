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
        self.__reasoning: dict = {} # dict of rule hits 
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

    # for print() output
    def __str__(self):
        # check if any rules were fired
        if len(self.__reasoning) > 0:
            outputReasoning = []

            for rule in self.__reasoning:
                outputReasoning.append(f"Rule {rule}: {self.__reasoning[rule]}")

            outputReasoning = "\n\t".join(outputReasoning)
        else:
            outputReasoning = "No rules were fired."

        # confidence ranges
        if 0.0 <= self.__confidence < 0.2:
            outputConfidence = f"Extremely unlikely to be a malicious or spam email. (Confidence score: {self.__confidence})"
        elif self.__confidence < 0.5:
            outputConfidence = f"Very unlikely to be a malicious or spam email. (Confidence score: {self.__confidence})"
        elif self.__confidence < 0.7:
            outputConfidence = f"Likely to be a malicious or spam email. (Confidence score: {self.__confidence})"
        elif self.__confidence < 0.9:
            outputConfidence = f"Very likely to be a malicious or spam email. (Confidence score: {self.__confidence})"
        elif self.__confidence <= 1.0:
            outputConfidence = f"Extremely likely to be a malicious or spam email. (Confidence score: {self.__confidence})"
        else:
            # this likely wouldn't happen at all
            raise ValueError(f"Invalid self.__confidence value of {self.__confidence} for file {self.__emlFile}.")

        return f"Successfully processed: {self.__emlFile}\nOutcome: {outputConfidence}\nRules Fired:\n\t{outputReasoning}"

    def __ParseEmlHeaders(self, filePath):
        if not os.path.exists(filePath):
            raise ValueError(f"Invalid file provided.")

        self.__emlFile = filePath
        parser = BytesFeedParser(policy=policy.default) # bytes parser for singular lines

        # read file in as bytes
        with open(self.__emlFile, 'rb') as emlFile:
            for line in emlFile:
                parser.feed(line) # feed single lines into parser

        self.__headers = parser.close() # parser.close() produces an EmailMessage object

        # check if any headers were processed
        if len(self.__headers.keys()) == 0:
            raise RuntimeError(f"Unable to parse input .eml file due to malformed headers or file is not a valid .eml file.")

        # email regex matching e.g. abc@xyz.com or abc@xyz.yyy.com
        emailRegex = re.compile(r"[A-Za-z0-9-_.]+@[A-Za-z0-9-]+\.(?:\.?[A-Za-z0-9-]+){1,}")

        # check for header defects
        if len(self.__headers.defects) > 0:
            self.__confidence += len(self.__headers.defects) * 0.5

            if len(self.__headers.defects) == 1:
                string = "malformed header"
            else:
                string = "malformed headers"

            self.__reasoning["-2"] = f"{len(self.__headers.defects)} {string} detected. (+{self.__confidence})"

        # loop through all sender and receiver headers
        for header in self.__ORIGINATOR_HEADERS + self.__DESTINATION_HEADERS:
            addresses = self.__headers.get_all(header)

            # extract email address only if header exists
            if addresses is not None:
                for address in addresses:
                    matches = emailRegex.findall(address)

                    if len(matches) > 0:
                        self.__headers.replace_header(header, matches)
                    else:
                        # if any address in the list cannot be parsed for any reason
                        if address == "" or address == None:
                            address = "None"

                        self.__confidence += 0.7

                        if not "-1" in self.__reasoning.keys():
                            self.__reasoning["-1"] = []

                        self.__reasoning["-1"].append(f"Invalid email address of {address} in the {header} header. (+0.7)")

                        if self.__confidence >= 1.0:
                            self.__confidence = 1.0
                            break
