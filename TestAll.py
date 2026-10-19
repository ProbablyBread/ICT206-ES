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

#            if eml.confidence > 0.0:
#                print("========")
#                print(f"{eml.emlFile}: {eml.confidence}")
#                print(f"{eml.reasoning}")
#                print("========\n\n")
            
            parsed += 1
        except Exception as e:
            errors += 1
            #print(f"Unhandled exception caught: {e}")

    print(f"Parsed {parsed} files over {(time.time() - start)} seconds.")
    print(f"Unable to parse {errors} files due to malformed .eml structure.")

def RunThat():
    engine = RuleEngine()

    eml = EmlES("./data/f0d0670b349aed344442f99f0c1a0c48.eml")
    #print(f"{eml.headers}\n")

    eml = EmlES("./data/f0b9ecc6869b31b80acccee9db0e2eb8.eml")
    #print(f"{eml.headers}\n")

    eml = EmlES("./data/0e132ee1bb9ad7f9764c6df9b22c7c75.eml")
    #print(f"{eml.headers}\n")

    eml = EmlES("./data/effe9e3b83a7cd1d1f63f1ac53fecfb0.eml")
    #print(f"{eml.headers}\n")

    eml = EmlES("./data/ef9850bb8526ba1e9526c715cd789b68.eml")
    #print(f"{eml.headers}\n")

    eml = EmlES("./data/eef075526b62f3abd00145392389f5e2.eml")
    #print(f"{eml.headers}\n")

    eml = EmlES("./data/d43e0d7b53cb8b94a28733db272ae769.eml")
    #print(f"{eml.headers}\n")
    #engine.Run(eml.headers)
    #print(eml.headers)
    #print("\n")
    #print(f"{eml.reasoning}, {eml.confidence}")

RunThis()
#RunThat()