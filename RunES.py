import os
import sys

try:
    from classes.EmlES import EmlES
except FileNotFoundError as e:
    print(f"FileNotFoundError: {e}")
    exit(1)
except RuntimeError as e:
    print(f"RuntimeError: {e}")
    exit(1)
except Exception as e:
    print(f"Unhandled exception caught: {e}")
    exit(1)

if len(sys.argv) == 1:
    filePath = input("Enter the relative or full path to an .eml file: ")
elif len(sys.argv) == 2:
    filePath = sys.argv[1]
else:
    print("Too many arguments provided.")
    exit(1)

filePath = filePath.replace('"', "").replace('"', "").strip()

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