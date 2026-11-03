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

import os
import time
import sys

if len(sys.argv) == 1:
    dir = input("Enter the relative or full path to a directory containing .eml files: ") 
elif len(sys.argv) == 2:
    dir = sys.argv[1]
else:
    print("Too many arguments provided.")
    exit(1)

start = time.time()

try:
    files = os.listdir(dir)
except Exception as e:
    print(f"Unable to list directory {dir}: {e}")
    exit(1)

parsed = 0
errors = 0

extremelyUnlikely = 0 
veryUnlikely = 0
likely = 0
veryLikely = 0
extremelyLikely = 0

for file in files:
    try:
        eml = EmlES(f"{dir}/{file}")
        confidence = eml.confidence

        if 0.0 <= confidence < 0.2:
            extremelyUnlikely += 1
        elif confidence < 0.5:
            veryUnlikely += 1
        elif confidence < 0.7:
            likely += 1
        elif confidence < 0.9:
            veryLikely += 1
        elif confidence <= 1.0:
            extremelyLikely += 1
        else:
            # this likely won't happen
            errors += 1
            continue

        parsed += 1

        if parsed % 50 == 0 or parsed == len(files):
            print(f"Progress: {parsed} of {len(files)}", end='\r')

    except Exception:
        errors += 1

print(f"Successfully parsed {parsed} files over {time.time() - start:.2f} seconds.")

if errors > 0:
    print(f"Errors were encountered parsing {errors} file(s).\n")
else:
    print("\n")

likelySummary = extremelyLikely + veryLikely + likely
unlikelySummary = veryUnlikely + extremelyUnlikely

print("Results: ")

if extremelyUnlikely > 0:
    print(f"{extremelyUnlikely} email(s) were detected to be extremely unlikely to be spam/malicious ({(extremelyUnlikely / parsed) * 100:.2f}%)")

if veryUnlikely > 0:
    print(f"{veryUnlikely} email(s) were detected to be very unlikely to be spam/malicious ({(veryUnlikely / parsed) * 100:.2f}%)")

if likely > 0:
    print(f"{likely} email(s) were detected to be likely to be spam/malicious ({(likely / parsed) * 100:.2f}%)")

if veryLikely > 0:
    print(f"{veryLikely} email(s) were detected to be very likely to be spam/malicious ({(veryLikely / parsed) * 100:.2f}%)")

if extremelyLikely > 0:
    print(f"{extremelyLikely} email(s) were detected to be extremely likely to be spam/malicious ({(extremelyLikely / parsed) * 100:.2f}%)")

print("\nSummary: ")

if likelySummary > 0:
    print(f"{likelySummary} email(s) were detected to be likely phishing ({likelySummary / parsed * 100:.2f}%)")

if unlikelySummary > 0:
    print(f"{unlikelySummary} email(s) were detected to be likely benign ({unlikelySummary / parsed * 100:.2f}%)")
