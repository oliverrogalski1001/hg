# hg (Fork)

# TapChecker Fork for Knox Evaluation

The original README is left below for reference. This repo modifies TapChecker's techniques for use in comparisons against Knox methods.

## Dependencies

These are left unchanged from the original implementation:

- The SMT solver Z3 (install via `pip install z3-solver`)
- `pymysql` used to connect to mySQL (install via `pip install pymysql`)
- `mysql` used for storing rule datasets (install and run `setup.sql` to load tables)

## Usage

Run `python3 main.py hg_timing` to get the runtime of the tapchecker algorithm for sceneId 1 and 3.

`tapchecker/mainCheck.py` contains the top level solver, modified to report all conflicts (rule violations) for TapChecker's 'Policy Conflict' checker only. The relevant code is in `tapchecker/optPolicyCon.py`.

### Algorithm Adjustments

Adjustments for evaluation against Knox can be run with `python3 main.py hg_adjusted`. Currently, Knox only runs routines from a given scene, which corresponds to a specific room in TapChecker's original experiments. Within a scene, all trigger conditions are ignored to maximize concurrency and conflict (rule violation) potential.

Modifications to the routine dataset are in the `knox_rule` table, which can be managed at `knox_table.sql`. Note this this pulls from `Data/experiment rules/t_rule.txt`, which has routines and triggers, but not device ID's. For checking those (to verify conflicts, for example), consult/launch a subquery against `t_action.txt`.

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
