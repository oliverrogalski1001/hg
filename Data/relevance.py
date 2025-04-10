import csv
import json
from collections import defaultdict
import random
import os
from string import Template
import subprocess

for filename in os.listdir():
    if os.path.isfile(filename):
        print(filename)
# process devices into dict deviceID -> device_dict
with open("experiment rules/t_device.txt") as f:
    f.readline()
    f.readline()
    headers = f.readline().strip().split("\t")

    reader = csv.reader(f, delimiter="\t")
    devices = {}
    cur_row = []
    skip = False
    for row in reader:
        if skip:
            cur_row += row
            skip = False
        elif not skip and len(row) != len(headers):
            cur_row = row
            skip = True
            continue
        else:
            cur_row = row

        device = {}
        deviceID = 0
        for i, header in enumerate(headers):
            if header == "deviceId":
                deviceID = int(cur_row[i])
            if cur_row[i].startswith("[") or cur_row[i].startswith("{"):
                try:
                    device[header] = json.loads(cur_row[i])
                except json.JSONDecodeError:
                    device[header] = cur_row[i]
            else:
                device[header] = cur_row[i]

        devices[deviceID] = device
        cur_row = []

# process triggers
with open("experiment rules/t_rule.txt") as f:
    f.readline()
    f.readline()
    headers = f.readline().strip().split("\t")

    reader = csv.reader(f, delimiter="\t")
    triggers = {}
    ruleID = 0
    for row in reader:
        trigger = {}
        for i, header in enumerate(headers):
            if header == "ruleID":
                deviceID = int(row[i])
            elif (header == "conditionIds" or header == "actionIds") and row[i].find(
                ","
            ):
                split = [int(num) for num in row[i].split(",")]
                trigger[header] = split
            else:
                trigger[header] = row[i]

        triggers[ruleID] = trigger
        ruleID += 1

# process condition
with open("experiment rules/t_condition.txt") as f:
    f.readline()
    f.readline()
    headers = f.readline().strip().split("\t")

    reader = csv.reader(f, delimiter="\t")
    conditions = {}
    for row in reader:
        condition = {}
        conditionID = 0
        for i, header in enumerate(headers):
            if len(row) != len(headers):
                continue
            if header == "conditionId":
                conditionID = int(row[i])
            elif header != "attribute":
                try:
                    num = int(row[i])
                except:
                    continue
                condition[header] = num
            else:
                condition[header] = row[i]

        conditions[conditionID] = condition

# process safety rules
with open("experiment rules/t_spec.txt") as f:
    f.readline()
    f.readline()
    headers = f.readline().strip().split("\t")

    reader = csv.reader(f, delimiter="\t")
    rules = []
    for row in reader:
        rule = {}
        for i, header in enumerate(headers):
            if header != "attribute1" and header != "attribute2":
                num = int(row[i])
                rule[header] = num
            else:
                rule[header] = row[i]

        rules.append(rule)


# process actions
with open("experiment rules/t_action.txt") as f:
    f.readline()
    f.readline()
    headers = f.readline().strip().split("\t")

    reader = csv.reader(f, delimiter="\t")
    actions = {}
    for row in reader:
        if len(row) != len(headers):
            continue
        action = {}
        actionID = 0
        for i, header in enumerate(headers):
            if header == "actionId":
                actionID = int(row[i])
            elif header != "attribute":
                try:
                    num = int(row[i])
                except:
                    continue
                action[header] = num
            else:
                action[header] = row[i]

        actions[actionID] = action

num_devices = 0
for deviceID, device in devices.items():
    if "readOnlyAttributes" in device:
        num_devices += len(device["readOnlyAttributes"])
    if "commonAttributes" in device:
        num_devices += len(device["commonAttributes"])

device_on_tree = set()


# build merge manager commands
def sample_routines(related_routines, all_routines, related_budget, all_budget):
    """
    Perform random sampling with replacement for the specified budgets.

    Args:
        related_routines (list): The first list to sample from.
        all_routines (list): The second list to sample from.
        related_budget (int): The number of samples to draw from related_routines.
        all_budget (int): The number of samples to draw from all_routines.

    Returns:
        tuple: Two lists containing the sampled items.
    """
    if not isinstance(related_budget, int) or not isinstance(all_budget, int):
        raise ValueError("Budgets must be integers.")
    if related_budget < 0 or all_budget < 0:
        raise ValueError("Budgets must be non-negative.")

    sampled_related = random.choices(related_routines, k=related_budget)
    sampled_all = random.choices(all_routines, k=all_budget)

    return sampled_related, sampled_all


for trail_idx in range(5):
    with open(f"large_full_commands{trail_idx}.txt", "w") as f:
        # construct merge manager object
        f.write(f"MergeManager manager({num_devices});\n")
        f.write("\n")

        # create devices
        device_attr = defaultdict(dict)
        cur_deviceID = 0
        for deviceID, device in devices.items():
            if "readOnlyAttributes" in device:
                for attr in device["readOnlyAttributes"]:
                    device_attr[deviceID][attr["name"].lower().strip()] = cur_deviceID
                    f.write(f"manager.createDevice({cur_deviceID}, {attr['num']});\n")
                    cur_deviceID += 1
            if "commonAttributes" in device:
                for attr in device["commonAttributes"]:
                    device_attr[deviceID][attr["name"].lower().strip()] = cur_deviceID
                    f.write(f"manager.createDevice({cur_deviceID}, {attr['num']});\n")
                    cur_deviceID += 1

        # build safety rule tree
        f.write("\n")
        cur_nodeID = 1
        for rule in rules:
            knox_deviceID1 = device_attr[rule["device1id"]][
                rule["attribute1"].lower().strip()
            ]
            knox_deviceID2 = device_attr[rule["device2id"]][
                rule["attribute2"].lower().strip()
            ]
            if rule["together"] == 0:  # NOT AND
                f.write(f"manager.addNode(0, {cur_nodeID}, NOT);\n")
                cur_nodeID += 1
                and_nodeID = cur_nodeID
                f.write(f"manager.addNode({cur_nodeID-1}, {cur_nodeID}, AND);\n")
                cur_nodeID += 1
                f.write(
                    f"manager.addLeaf({and_nodeID}, {cur_nodeID}, {knox_deviceID1}, {rule['newValue1']});\n"
                )
                cur_nodeID += 1
                f.write(
                    f"manager.addLeaf({and_nodeID}, {cur_nodeID}, {knox_deviceID2}, {rule['newValue2']});\n"
                )
                cur_nodeID += 1
                device_on_tree.add(knox_deviceID1)
                device_on_tree.add(knox_deviceID2)

            elif rule["together"] == 1:  # IMPLIES, NOT P OR Q
                or_nodeID = cur_nodeID
                f.write(f"manager.addNode(0, {cur_nodeID}, OR);\n")
                cur_nodeID += 1
                f.write(f"manager.addNode({or_nodeID}, {cur_nodeID}, NOT);\n")
                cur_nodeID += 1
                f.write(
                    f"manager.addLeaf({cur_nodeID-1}, {cur_nodeID}, {knox_deviceID1}, {rule['newValue1']});\n"
                )
                cur_nodeID += 1
                f.write(
                    f"manager.addLeaf({or_nodeID}, {cur_nodeID}, {knox_deviceID2}, {rule['newValue2']});\n"
                )
                cur_nodeID += 1
                device_on_tree.add(knox_deviceID1)
                device_on_tree.add(knox_deviceID2)

        related_routines = []
        all_routines = []
        # build routines
        f.write("\n")

        for triggerID, trigger in triggers.items():
            actionID = trigger["actionIds"][0]
            action = actions[actionID]
            knox_deviceID = device_attr[action["deviceId"]][
                action["attribute"].lower().strip()
            ]

            routine_string = f" = {{{{{knox_deviceID},{action['newValue']}}}}};\n"
            # routine r{cur_routineID}
            all_routines.append(routine_string)
            if knox_deviceID in device_on_tree:
                related_routines.append(routine_string)

        selected_related, selected_all = sample_routines(
            related_routines, all_routines, 500, 0
        )
        for cur_routineID, routine in enumerate(selected_related):
            f.write(f"routine r{cur_routineID}{routine}")
            f.write(f"manager.addRoutine(r{cur_routineID});\n")

        for cur_routineID, routine in enumerate(
            selected_all, start=len(selected_related)
        ):
            f.write(f"routine r{cur_routineID}{routine}")
            f.write(f"manager.addRoutine(r{cur_routineID});\n")


with open("cmain_template.txt", "r") as f:
    template = Template(f.read())

eval_csv = open("eval/large_full.csv", "w")
writer = csv.writer(eval_csv)
writer.writerow(["algorithm", "time", "check count"])

for trail_idx in range(5):
    with open(f"large_full_commands{trail_idx}.txt", "r") as f:
        merge_manager_text = f.read()

    with open("../../KNOX_Perf/rel.cpp", "w") as f:
        f.write(template.substitute(merge_manager=merge_manager_text))

    subprocess.run(["make"], cwd="../../KNOX_Perf/build")
    res = subprocess.run(
        ["./relevance"], cwd="../../KNOX_Perf/build", capture_output=True, text=True
    ).stdout
    for algorithm_res in res.split("\n")[:-1]:
        writer.writerow(algorithm_res.split(","))

eval_csv.close()
