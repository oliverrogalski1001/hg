# -*- coding:utf-8 -*-
from functools import reduce
from os import curdir
import os
import pymysql
from z3 import *


def connect():
    # Defaults match a local MySQL with the upstream settings; override with HG_DB_* variables.
    return pymysql.connect(
        host=os.environ.get("HG_DB_HOST", "localhost"),
        port=int(os.environ.get("HG_DB_PORT", "3306")),
        user=os.environ.get("HG_DB_USER", "root"),
        password=os.environ.get("HG_DB_PASSWORD", ""),
        database=os.environ.get("HG_DB_NAME", "hg"),
    )


# ['ruleId', 'ruleName', 'conditionIds', 'actionIds','dayofweeks','starttime','endtime']
def getAllRules(db, sceneId="", userId=""):
    cursor = db.cursor()
    if userId != "" and sceneId != "":
        try:
            cursor.execute(
                "SELECT * FROM t_rule WHERE userId = '"
                + str(userId)
                + "' AND sceneId = '"
                + str(sceneId)
                + "'"
            )
            rule = cursor.fetchall()
        except:
            rule = []
    elif userId != "":
        try:
            cursor.execute("SELECT * FROM t_rule WHERE userId = '" + str(userId) + "'")
            rule = cursor.fetchall()
        except:
            rule = []
    elif sceneId != "":
        try:
            cursor.execute(
                "SELECT * FROM t_rule WHERE sceneId = '" + str(sceneId) + "'"
            )
            rule = cursor.fetchall()
        except:
            rule = []
    else:
        cursor.execute("SELECT * FROM t_rule")
        rule = cursor.fetchall()
    return rule


def getRandomRules(db, sceneId=3, numRules=5, seed=None):
    cursor = db.cursor()
    try:
        cursor.execute(f"""
            SELECT t_rule.*
            FROM t_rule
            INNER JOIN t_action ON t_rule.actionIds = t_action.actionId
            WHERE t_rule.sceneId = {sceneId}
            AND (t_action.deviceId, t_action.attribute)  IN (
                SELECT DISTINCT t_action.deviceId, t_action.attribute
                FROM t_action
                INNER JOIN t_rule ON t_rule.actionIds = t_action.actionId
                WHERE t_action.actionId IN (SELECT actionIds FROM t_rule WHERE ruleId IN (224,2217,1761,1170,1600,1103,660,789,824,1022,1087,1270))
            )
            ORDER BY RAND({'' if seed is None else int(seed)})
            LIMIT {numRules}
        """)
        rule = cursor.fetchall()
    except:
        rule = []
    return rule


def getSomeRules(db, sceneId="", userId="", ruleIds=[]):
    cursor = db.cursor()
    if userId != "" and sceneId != "":
        try:
            cursor.execute(
                "SELECT * FROM t_rule WHERE userId = '"
                + str(userId)
                + "' AND sceneId = '"
                + str(sceneId)
                + f"' AND ruleId IN ({','.join([str(rule) for rule in ruleIds])})"
            )
            rule = cursor.fetchall()
        except:
            rule = []
    elif userId != "":
        try:
            cursor.execute(
                "SELECT * FROM t_rule WHERE userId = '"
                + str(userId)
                + "'"
                + f" AND ruleId IN ({','.join([str(rule) for rule in ruleIds])})"
            )
            rule = cursor.fetchall()
        except:
            rule = []
    elif sceneId != "":
        try:
            cursor.execute(
                "SELECT * FROM t_rule WHERE sceneId = '"
                + str(sceneId)
                + "'"
                + f" AND ruleId IN ({','.join([str(rule) for rule in ruleIds])})"
            )
            rule = cursor.fetchall()
        except:
            rule = []
    else:
        cursor.execute("SELECT * FROM t_rule")
        rule = cursor.fetchall()
    return rule


# def getAllRules(db,userId,sceneId):
#     cursor = db.cursor()
#     rule = []
#     if userId and sceneId:
#         try:
#             cursor.execute("SELECT * FROM t_rule WHERE userId = '" + str(userId) +\
#                  "' AND sceneid = '" + str(sceneId) + "'")
#             rule = cursor.fetchall()
#         except:
#             pass
#     return rule


# ['conditionIds', 'deviceId', 'attribute', 'compareType', 'standardValue']
def getCondition(Cid, db):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM t_condition WHERE conditionId = '" + str(Cid) + "'")
    con = cursor.fetchone()
    if con == None:
        con = True
    return con


def getConbyDev(Did, db):
    Did = str(Did)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM t_condition WHERE deviceId = '" + str(Did) + "'")
    con = cursor.fetchall()
    if con == None:
        con = True
    # db.close()
    return con


# ['actionId', 'deviceId', 'attribute', 'newValue', 'oldValue']
def getAction(Aid, db):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM t_action WHERE actionId = '" + str(Aid) + "'")
    act = cursor.fetchone()
    if act == None:
        act = True
    return act


def getActbyDev(Did, db):
    Did = str(Did)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM t_action WHERE deviceId = '" + str(Did) + "'")
    act = cursor.fetchall()
    if act == None:
        act = True
    return act


def getActbyAttr(a1, a2, a3, db):
    cursor = db.cursor()
    cursor.execute(
        "SELECT actionId FROM t_action WHERE deviceId = '"
        + str(a1)
        + "'"
        + " and attribute = '"
        + str(a2)
        + "'"
        + "and newValue = '"
        + str(a3)
        + "'"
    )
    act = cursor.fetchall()
    return act


def getRule(Rid, db):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM t_rule WHERE ruleId = '" + str(Rid) + "'")
    rl = cursor.fetchone()
    if rl == None:
        rl = True
    return rl


# deviceId deviceUuid deviceName categoryId readOnlyId readOnlyAttributes commonAttributes
def getDevice(Did, db):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM t_device WHERE deviceId = '" + str(Did) + "'")
    dev = cursor.fetchone()
    if dev == None:
        dev = True
    return dev


# ['actionId', 'deviceId', 'attribute', 'newValue']
def getDevEffect(Did, attribute, newValue, db):
    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM t_entity WHERE deviceId = '"
        + str(Did)
        + "'"
        + "and attribute = '"
        + str(attribute)
        + "'"
        + "and newValue = '"
        + str(newValue)
        + "'"
    )
    effect = cursor.fetchone()
    return effect


# 获取所有specification
def getAllSpec(db):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM t_spec")
    spec = cursor.fetchall()
    return spec


#
def getSpecAction(spec, db):
    actId = []
    cursor = db.cursor()
    cursor.execute(
        "SELECT actionId FROM t_action WHERE deviceId = '"
        + str(spec[0])
        + "'"
        + "and attribute = '"
        + str(spec[1])
        + "' and newValue = '"
        + str(spec[2])
        + "'"
    )
    act = cursor.fetchall()
    for a in act:
        actId.append(str(a[0]))
    return actId


def getSpecCon(spec, db):
    conId = []
    cursor = db.cursor()
    cursor.execute(
        "SELECT conditionId FROM t_condition WHERE deviceId = '"
        + str(spec[0])
        + "'"
        + "and attribute = '"
        + str(spec[1])
        + "' and standardValue = '"
        + str(spec[2])
        + "'"
    )
    con = cursor.fetchall()
    for c in con:
        conId.append(str(c[0]))
    return conId


def getNotCon(spec, db):
    conId = []
    cursor = db.cursor()
    cursor.execute(
        "SELECT actionId FROM t_action WHERE deviceId = '"
        + str(spec[0])
        + "'"
        + "and attribute = '"
        + str(spec[1])
        + "' and newValue <> '"
        + str(spec[2])
        + "'"
    )
    actId = cursor.fetchall()
    if str(actId) != "()":
        for aid in actId:
            cursor.execute(
                "SELECT conditionId FROM t_rule WHERE actionIds = '" + str(aid) + "'"
            )
            cid = cursor.fetchall()
            for c in cid:
                conId.append(str(c[0]))
    return conId


# 把条件转换成Z3表达式
# ['conditionIds', 'deviceId', 'attribute', 'compareType', 'standardValue']
def conditionToZ3(condition):
    if not condition == None and not condition == True:
        x = Int((str(condition[1]) + ":" + str(condition[2])).encode("utf-8"))
        # print(condition[4])
        # 1是等于
        if condition[3] == 1:
            con = x == condition[4]
        # 2是大于
        elif condition[3] == 2:
            con = x > condition[4]
        # 3是小于
        elif condition[3] == 3:
            con = x < condition[4]
        # 4是大于等于
        elif condition[3] == 4:
            con = x >= condition[4]
        # 5是小于等于
        elif condition[3] == 5:
            con = x <= condition[4]
        # 6是不等于
        elif condition[3] == 6:
            con = x != condition[4]
        else:
            con = False
        return con
    else:
        return True


# 把动作转换成Z3表达式
# ['actionId', 'deviceId', 'attribute', 'newValue']
def actionToZ3(action):
    if action == None:
        return True
    x = Int((str(action[1]) + ":" + action[2]).encode("utf-8"))
    act = x == action[3]
    return act


def ConditionsImplie(con1, con2, db):
    s = Solver()
    a = True
    b = True
    for c1 in con1:
        c1z = conditionToZ3(getCondition(c1, db))
        a = And(a, c1z)
    for c2 in con2:
        c2z = conditionToZ3(getCondition(c2, db))
        b = And(b, c2z)
    if s.check(Not(Implies(a, b))) == unsat:
        return True
    return False


def getPolicy(db):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM t_spec")
    specs = cursor.fetchall()
    policies = []
    for spec in specs:
        x = Int((str(spec[0]) + ":" + str(spec[1])).encode("utf-8")) == spec[2]
        y = Int((str(spec[3]) + ":" + str(spec[4])).encode("utf-8")) == spec[5]
        if spec[6] == 0:
            policies.append(Not(And(x, y)))
        else:
            policies.append(Implies(x, y))
    return policies


def getEffect(db):
    # cursor = db.cursor()
    # cursor.execute("SELECT * FROM t_entity")
    # entities = cursor.fetchall()
    effects = []
    x1 = Int("79:设备状态".encode("utf-8")) == 3
    y1 = Int("88:温度".encode("utf-8")) > 26
    effects.append(Implies(x1, y1))
    x2 = Int("79:设备状态".encode("utf-8")) == 4
    y2 = Int("88:温度".encode("utf-8")) < 26
    effects.append(Implies(x2, y2))
    x3 = Int("84:设备状态".encode("utf-8")) == 1
    effects.append(Implies(x3, y1))

    x1 = Int("99:设备状态".encode("utf-8")) == 3
    y1 = Int("105:温度".encode("utf-8")) > 26
    effects.append(Implies(x1, y1))
    x2 = Int("99:设备状态".encode("utf-8")) == 4
    y2 = Int("105:温度".encode("utf-8")) < 26
    effects.append(Implies(x2, y2))
    x3 = Int("103:设备状态".encode("utf-8")) == 1
    effects.append(Implies(x3, y1))

    x1 = Int("116:设备状态".encode("utf-8")) == 3
    y1 = Int("119:温度".encode("utf-8")) > 26
    effects.append(Implies(x1, y1))
    x2 = Int("116:设备状态".encode("utf-8")) == 4
    y2 = Int("119:温度".encode("utf-8")) < 26
    effects.append(Implies(x2, y2))
    x3 = Int("117:设备状态".encode("utf-8")) == 1
    effects.append(Implies(x3, y1))
    return effects
