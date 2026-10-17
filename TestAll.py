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
        eml = EmlES(f"{dir}/{file}")

        #print("========")
        #print(eml)
        #print("========\n\n")
        
        num += 1
    except RuntimeError as e:
        print(f"RuntimeError: {e}")
    except Exception as e:
        print(f"Unhandled exception caught: {e}")

print(f"Elapsed over {num} files: {(time.time() - start)} seconds")

# file with invalid bytes
#eml = EmlES("./data/1eb99ffccafed8b65200d701dcaffe7a.eml")
#print(eml)