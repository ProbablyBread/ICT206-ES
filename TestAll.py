try:
    from EmlES import EmlES
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

start = time.time()

dir = "./data"
parsed = 0
errors = 0

for file in os.listdir(dir):
    try:
        eml = EmlES(f"{dir}/{file}")

        print("========")
        print(eml.headers)
        print(eml.emlFile)
        print("========\n\n")
        
        parsed += 1
    except RuntimeError as e:
        errors += 1
    except ValueError as e:
        errors += 1
    except Exception as e:
        errors += 1
        print(f"Unhandled exception caught: {e}")

print(f"Parsed {parsed} files over {(time.time() - start)} seconds.")
print(f"Unable to parse {errors} files due to malformed .eml structure.")

#eml = EmlES("./data/f0d0670b349aed344442f99f0c1a0c48.eml")
#print(eml.headers)
#
#eml = EmlES("./data/f0b9ecc6869b31b80acccee9db0e2eb8.eml")
#print(eml.headers)
#
#eml = EmlES("./data/0e132ee1bb9ad7f9764c6df9b22c7c75.eml")
#print(eml.headers)