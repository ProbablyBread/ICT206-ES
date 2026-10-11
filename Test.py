from EmlES import EmlES
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
        print(f"ERROR: {e} on file {file}")

print(f"Elapsed over {num} files: {(time.time() - start)} seconds")

# file with invalid bytes
#eml = EmlES("./data/1eb99ffccafed8b65200d701dcaffe7a.eml")
#print(eml)