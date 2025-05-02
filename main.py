import sys
from tapchecker import mainCheck
from tapchecker import connectAndTransfer as cat

if len(sys.argv) != 2:
    print("usage: python3 main.py [test_name]")
    print("test_name = {hg, hg_adjusted}")

if sys.argv[1] == "hg":
    res = mainCheck.check(cat.connect(), sceneId=3)
elif sys.argv[1] == "hg_adjusted":
    res = mainCheck.check(cat.connect(), sceneId=3, adjusted=True)
else:
    print("unknown test_name")

print(f"took {res["times"]} seconds")
print("\n".join(res["conflicts"]))
