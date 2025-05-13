import sys
from tapchecker import mainCheck
from tapchecker import connectAndTransfer as cat

if len(sys.argv) != 2:
    print("usage: python3 main.py [test_name]")
    print("test_name = {hg_timing, hg_adjusted}")

if sys.argv[1] == "hg_timing":
    res = mainCheck.check(cat.connect(), sceneId=1)
    print(f"took {res["times"]} seconds")
    res = mainCheck.check(cat.connect(), sceneId=3)
    print(f"took {res["times"]} seconds")
elif sys.argv[1] == "hg_adjusted":
    res = mainCheck.check(cat.connect(), sceneId=3, adjusted=True)
    print(f"took {res["times"]} seconds")
    print("\n".join(res["conflicts"]))
else:
    print("unknown test_name")
