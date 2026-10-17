try:
    from EmlES import EmlES
except FileNotFoundError as e:
    print(f"FileNotFoundError: {e}")
    exit(1)
except SyntaxError as e:
    print(f"SyntaxError: {e}")
    exit(1)
except Exception as e:
    print(f"Unhandled exception caught: {e}")
    exit(1)

import os
import time

start = time.time()

dir = "./data"
num = 0

for file in os.listdir(dir):
    try:
        #eml = EmlES(f"{dir}/{file}")

        #print("========")
        #print(eml)
        #print("========\n\n")
        
        num += 1
    except RuntimeError as e:
        print(f"RuntimeError: {e}")
    except Exception as e:
        print(f"Unhandled exception caught: {e}")

    #if eml.confidence == 1:
        #print(f"{file}: {eml.reasoning}")

print(f"Elapsed over {num} files: {(time.time() - start)} seconds")

#eml = EmlES("./data/f0d0670b349aed344442f99f0c1a0c48.eml")
eml = EmlES("./data/f0b9ecc6869b31b80acccee9db0e2eb8.eml")
print(eml.headers)