import os
import re

class EmlES:
    def __init__(self):
        self.__confidence: float = 0.0 # confidence rating
        self.__emlFile: str = "None" # path to .eml file
        self.__headers: dict[str] = {} # eml file headers

    def __eq__(self, other):
        if not self.__class__ is other.__class__:
            return NotImplemented
        else:
            return self.__emlFile == other.__emlFile

    def __str__(self):
        return f"""Headers: {self.__headers}
File Path: {self.__emlFile}
Confidence: {self.__confidence}
"""

    def Run(self, filePath):
        self.__ParseEmlFile(filePath)

    def __ParseHeaders(self, headerString):
        if re.match(r"^[A-Za-z-]+:\s?.*$", headerString):
            parts = headerString.split(":", 1)
            return parts[0], parts[1].strip()
        else:
            raise ValueError("Invalid header string format")

    def __ParseEmlFile(self, filePath):
        if os.path.isfile(filePath) and os.path.exists(filePath) and filePath.endswith(".eml"):
            ctype = "" # store content type string

            # read whole file
            with open(filePath, 'r') as eml:
                contents = eml.readlines()

            # parse each line until a single \n
            for line in contents:
                if line == "\n":
                    break

                if line.lower().startswith("content-type") or line.lower().startswith("\t"):
                    ctype += line.strip() # collect all the content-type into a single line
                else:
                    try:
                        key, value = self.__ParseHeaders(line)
                        self.__headers[key] = value
                    except ValueError:
                        pass

            # parse the content-type
            try:
                key, value = self.__ParseHeaders(ctype)
                self.__headers[key] = value
            except ValueError:
                pass
        else:
            raise RuntimeError("Invalid .eml file supplied.")

        # check if from, to, and subject headers exist
        if not set(["From", "To", "Subject"]).issubset(self.__headers.keys()):
            raise RuntimeError("Invalid .eml file supplied.")

        # set the file name in the class
        self.__emlFile = filePath
