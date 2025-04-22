import csv
import json
from collections import defaultdict

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

# count how many devices we need
num_devices = 0
for deviceID, device in devices.items():
    if "readOnlyAttributes" in device:
        num_devices += len(device["readOnlyAttributes"])
    if "commonAttributes" in device:
        num_devices += len(device["commonAttributes"])

# build merge manager commands
with open("commands.txt", "w") as f:
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
                f.write(f"manager.createDevice({cur_deviceID}, {attr["num"]});\n")
                cur_deviceID += 1
        if "commonAttributes" in device:
            for attr in device["commonAttributes"]:
                device_attr[deviceID][attr["name"].lower().strip()] = cur_deviceID
                f.write(f"manager.createDevice({cur_deviceID}, {attr["num"]});\n")
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
                f"manager.addLeaf({and_nodeID}, {cur_nodeID}, {knox_deviceID1}, {rule["newValue1"]});\n"
            )
            cur_nodeID += 1
            f.write(
                f"manager.addLeaf({and_nodeID}, {cur_nodeID}, {knox_deviceID2}, {rule["newValue2"]});\n"
            )
            cur_nodeID += 1

        elif rule["together"] == 1:  # IMPLIES, NOT P OR Q
            or_nodeID = cur_nodeID
            f.write(f"manager.addNode(0, {cur_nodeID}, OR);\n")
            cur_nodeID += 1
            f.write(f"manager.addNode({or_nodeID}, {cur_nodeID}, NOT);\n")
            cur_nodeID += 1
            f.write(
                f"manager.addLeaf({cur_nodeID-1}, {cur_nodeID}, {knox_deviceID1}, {rule["newValue1"]});\n"
            )
            cur_nodeID += 1
            f.write(
                f"manager.addLeaf({or_nodeID}, {cur_nodeID}, {knox_deviceID2}, {rule["newValue2"]});\n"
            )
            cur_nodeID += 1

    # build routines
    f.write("\n")
    cur_routineID = 0
    for triggerID, trigger in triggers.items():
        actionID = trigger["actionIds"][0]
        action = actions[actionID]
        knox_deviceID = device_attr[action["deviceId"]][
            action["attribute"].lower().strip()
        ]
        f.write(
            f"routine r{cur_routineID} = {{{{{knox_deviceID},{action["newValue"]}}}}};\n"
        )
        f.write(f"manager.addRoutine(r{cur_routineID});\n")
        cur_routineID += 1
