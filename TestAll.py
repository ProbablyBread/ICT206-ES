try:
    from EmlES import EmlES
    from RuleEngine import RuleEngine
except FileNotFoundError as e:
    print(f"FileNotFoundError: {e}")
    exit(1)
except RuntimeError as e:
    print(f"RuntimeError: {e}")
    exit(1)
except Exception as e:
    print(f"Unhandled exception caught: {e}")
    exit(1)

import os
import time

def RunThis():
    start = time.time()

    dir = "./data"
    parsed = 0
    errors = 0

    for file in os.listdir(dir):
        try:
            eml = EmlES(f"{dir}/{file}")

            if eml.confidence == 1.0:
                print("========")
                print(f"{eml.emlFile}: {eml.confidence}")
                print(f"{eml.reasoning}")
                print("========\n\n")
            
            parsed += 1
        except Exception as e:
            errors += 1
            #print(f"Unhandled exception caught: {e}")

    print(f"Parsed {parsed} files over {(time.time() - start)} seconds.")
    print(f"Unable to parse {errors} files due to malformed .eml structure.")

def RunThat():
    eml = EmlES("./data/f0b9ecc6869b31b80acccee9db0e2eb8.eml")
    print(f"{eml.headers.get_all("From")}\n")
    print(f"{eml.reasoning}")

#RunThis()
RunThat()