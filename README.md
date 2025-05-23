# hg (Fork)

# TapChecker Fork for Knox Evaluation

The original README is left below for reference. This repo modifies TapChecker's techniques for use in comparisons against Knox methods.

## Dependencies

These are left unchanged from the original implementation:

- The SMT solver Z3 (install via `pip install z3-solver`)
- `pymysql` used to connect to mySQL (install via `pip install pymysql`)
- `mysql` used for storing rule datasets (install and run `setup.sql` to load tables)

## Usage

Load the dataset into MySQL by running `setup.sql` from the repository root (its `Data/...` paths are relative, and it needs `local_infile` on). `tapchecker/connectAndTransfer.py` connects to database `hg` on `localhost:3306` as `root` with an empty password; set `HG_DB_HOST`, `HG_DB_PORT`, `HG_DB_USER`, `HG_DB_PASSWORD` or `HG_DB_NAME` to change that.

`python3 main.py -h` lists the experiments and options.

### Knox paper, Table IX (runtime)

```sh
python3 main.py hg_timing --k 50 --seed 1
python3 main.py hg_timing --k 500 --seed 1
```

For the living room (sceneId 1, LR) and the bedroom (sceneId 3, BR), this samples K rules with replacement and prints the time of TapChecker's policy-conflict check (`optPolicyCon.f`) on them. The time covers the check only, not loading rules or building Z3 expressions. Without `--k`, every rule in the scene is checked.

### Knox paper, Table X (false negatives)

```sh
python3 main.py hg_fn 100 12 --three-way 1 --seed 1
python3 main.py hg_fn 100 12 --three-way 3 --seed 1
python3 main.py hg_fn 100 12 --three-way 4 --seed 1
```

Each trial checks the rules in `FN_routines.txt` plus `routines_added` (12 above, 29 rules in total) random bedroom rules that act on the same device attributes as its first 12 rules. The safety policies are TapChecker's plus the first N three-way rules in `main.py` (`--three-way N`). `f_triple` reports conflicts among up to three rules; a reported conflict that contains no pairwise conflict from `f_adjusted` is a false negative of the pairwise check. The script prints two rates per trial and their averages:

- `FN rate` counts every ordering of a rule combination separately
- `unique combinations` counts each combination once

`--seed S` seeds the sampling with MySQL `RAND(S + trial)`, so a run repeats on the same dataset load and MySQL version.

### Knox paper, Hardware

Apple M1, Python 3.13, z3-solver 5.1.0, MySQL 9.5, `--seed 1`.

### Algorithm Adjustments

Adjustments for evaluation against Knox can be run with `python3 main.py hg_adjusted`. Currently, Knox only runs routines from a given scene, which corresponds to a specific room in TapChecker's original experiments. Within a scene, all trigger conditions are ignored to maximize concurrency and conflict (rule violation) potential.

Modifications to the routine dataset are in the `knox_rule` table, which can be managed at `knox_table.sql`. Pulls from `Data/experiment rules/t_rule.txt`, which has routines and triggers, but not device ID's.

Finally, to see all safety rules, see `Data/experiment rules/t_spec.txt`.

# This is the core algorithm used by HomeGuard. The program entry is the main.py file

The main package that the program depends on is Z3, which can be installed using the code 'pip install z3-solver'.

The experiment rules data in the Data folder is exported from the mysql database. You can import into your own local mysql database using the `setup.sql` script and configure your database information in the connectAndTransfer.py file. This allows the code to connect to your database for user rules reading.
The operation of the mysql database can install dependencies through the code 'pip install pymysql'

========================================================
The ActCon.py file is the algorithm used to detect Action Conflicts.
The AlwaysTrue.py file is the algorithm used to detect Unconditional Triggering.
The PolicyCon.py file is the code used to detect Device Conflicts.
The SelfCon.py file is the algorithm used to detect Self Conflicts.
The TACon.py file is the algorithm used to detect Cyclic Triggering.
The Redundancy.py file is the algorithm used to detect Redundant Rules.

connectAndTransfer.py contains some tool functions used in the detection process, including functions that interact with the database, functions that involve format conversion, etc.
