import os

from classes.EmlES import EmlES

filePath = input("Enter the relative or full path to an .eml file: ")
filePath = filePath.replace('"', "").replace('"').strip()

if not os.path.exists(filePath):
    print(f"ERROR: {filePath} does not exist.")
    exit(1)
elif not os.path.isfile(filePath):
    print(f"ERROR: {filePath} does not appear to be a file.")
    exit(1)

try:
    eml = EmlES(filePath)
    print(f"\n{eml}")
except Exception as e:
    print(f"Error processing {filePath}.\n{e}")
    exit(1)