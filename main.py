from tapchecker import mainCheck
from tapchecker import connectAndTransfer as cat

# trials = 3
# for _ in range(trials):
#     print(f"scene 1: {mainCheck.check(cat.connect(), "", 1)["times"][0]}s")

# for _ in range(trials):
#     print(f"scene 3: {mainCheck.check(cat.connect(), "", 3)["times"][2]}s")

res = mainCheck.check(cat.connect())
print("\n".join(res["conflicts"]))
