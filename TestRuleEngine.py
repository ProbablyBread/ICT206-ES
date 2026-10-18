from RuleEngine import RuleEngine

try:
    r = RuleEngine()
    r.Run({})
except Exception as e:
    print(e)