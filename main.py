from EmlES import EmlES

try:
    asdf = EmlES()
    asdf.Run("./data/0a0b6e855d85c7d069d89f3db07384df.eml")
    print(asdf)
except RuntimeError as e:
    print(f"ERROR: {e}")