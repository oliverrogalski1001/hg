from tapchecker import mainCheck
from tapchecker import connectAndTransfer as cat

res = mainCheck.check(cat.connect())
print("\n".join(res["conflicts"]))
