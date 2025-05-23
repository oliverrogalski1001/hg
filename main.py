import argparse
import random
from z3 import *
from tapchecker import mainCheck
from tapchecker import connectAndTransfer as cat
from tapchecker import optPolicyCon

# Three-way safety rules for hg_fn (paper Table X), each "if x then not (y and z)" over
# (device:attribute, value) pairs. --three-way N adds the first N.
THREE_WAY_RULES = [
    (("115:equipment status", 1), ("122:equipment status", 1), ("119:equipment status", 2)),
    (("121:equipment status", 2), ("111:equipment status", 1), ("112:equipment status", 1)),
    (("112:equipment status", 2), ("115:timing", 4), ("118:equipment status", 1)),
    (("120:volume", 11), ("113:equipment status", 2), ("121:equipment status", 2)),
]


def three_way_policies(n):
    policies = []
    for (xv, xs), (yv, ys), (zv, zs) in THREE_WAY_RULES[:n]:
        x = Int(xv) == xs
        y = Int(yv) == ys
        z = Int(zv) == zs
        policies.append(Implies(x, Not(And(y, z))))
    return policies


def read_rule_ids(path):
    with open(path, "r") as f:
        return [int(line) for line in f if line.strip()]


def fn_rate(triple_conflicts, base_conflicts):
    # Fraction of f_triple conflicts that contain no pairwise (f_adjusted) conflict.
    if len(triple_conflicts) == 0:
        return 0.0
    count = 0
    for conf_triple in triple_conflicts:
        contained = False
        for conf in base_conflicts:
            if conf[0] in conf_triple and conf[1] in conf_triple:
                contained = True
        count += not contained
    return count / len(triple_conflicts)


def unique_conflicts(conflicts):
    # 46eaa22 collected conflicts in a set of sorted tuples: one entry per rule combination.
    return {tuple(sorted(conf)) for conf in conflicts}


parser = argparse.ArgumentParser(description="TapChecker experiments for the Knox comparison")
parser.add_argument("test_name", choices=["hg_timing", "hg_adjusted", "hg_sample", "hg_fn"])
parser.add_argument("trials", type=int, nargs="?", help="hg_fn: number of trials")
parser.add_argument(
    "routines_added", type=int, nargs="?", help="hg_fn: random sceneId 3 rules added per trial"
)
parser.add_argument(
    "--three-way",
    type=int,
    default=1,
    choices=range(len(THREE_WAY_RULES) + 1),
    metavar="N",
    help="hg_fn: number of three-way rules to add (paper Table X: 1, 3, 4; default 1)",
)
parser.add_argument(
    "--k",
    type=int,
    help="hg_timing: sample K rules with replacement from each scene (paper Table IX: 50, 500)",
)
parser.add_argument(
    "--seed",
    type=int,
    help="seed rule sampling (hg_fn: MySQL RAND(seed + trial); hg_timing: Python random)",
)
args = parser.parse_args()

if args.test_name == "hg_timing":
    random.seed(args.seed)
    db = cat.connect()
    # sceneId 1 is the living room (LR), sceneId 3 the bedroom (BR).
    for sceneId in (1, 3):
        appletsList = mainCheck.getAppletList(db, sceneId=sceneId)
        if args.k is not None:
            appletsList = random.choices(appletsList, k=args.k)
        res = mainCheck.check(db, appletsList)
        print(f"sceneId {sceneId}: {len(appletsList)} rules, took {res['times']} seconds")
elif args.test_name == "hg_adjusted":
    db = cat.connect()
    appletsList = mainCheck.getAppletList(db, sceneId=3)
    res = mainCheck.check(db, appletsList=appletsList, checker=optPolicyCon.f_adjusted)
    print(f"took {res['times']} seconds")
    print(res["conflicts"])
elif args.test_name == "hg_sample":
    db = cat.connect()
    ruleIds = read_rule_ids("routines.txt")
    appletsList = mainCheck.getAppletList(db, sceneId=3, ruleIds=ruleIds)
    res = mainCheck.check(db, appletsList=appletsList)
    print(res["conflicts"])
elif args.test_name == "hg_fn":
    if args.trials is None or args.routines_added is None:
        parser.error("hg_fn needs trials and routines_added")
    db = cat.connect()
    ruleIds = read_rule_ids("FN_routines.txt")
    additionalPolicy = three_way_policies(args.three_way)
    fn_rate_count = 0
    unique_fn_rate_count = 0
    for i in range(args.trials):
        appletsList = mainCheck.getAppletList(db, sceneId=3, ruleIds=ruleIds)
        seed = None if args.seed is None else args.seed + i
        appletsList += cat.getRandomRules(db, 3, args.routines_added, seed=seed)
        if i == 0:
            print(f"# routines = {len(appletsList)}")
        res_triple = mainCheck.check(
            db,
            appletsList=appletsList,
            checker=optPolicyCon.f_triple,
            additionalPolicy=additionalPolicy,
        )
        res_base = mainCheck.check(
            db,
            appletsList=appletsList,
            checker=optPolicyCon.f_adjusted,
            additionalPolicy=additionalPolicy,
        )
        rate = fn_rate(res_triple["conflicts"], res_base["conflicts"])
        unique_rate = fn_rate(unique_conflicts(res_triple["conflicts"]), res_base["conflicts"])
        fn_rate_count += rate
        unique_fn_rate_count += unique_rate
        print(f"FN rate = {rate} (unique combinations: {unique_rate})")
    print(f"Average FN rate over {args.trials} trials = {fn_rate_count / args.trials}")
    print(f"Average FN rate over unique combinations = {unique_fn_rate_count / args.trials}")
