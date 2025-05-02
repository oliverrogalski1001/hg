# -*- coding:utf-8 -*-
from z3 import *
from tapchecker import connectAndTransfer as cat
import pymysql
import time
from functools import reduce
from tapchecker import optActCon
from tapchecker import optAlwaysTrue
from tapchecker import optPolicyCon
from tapchecker import optRedundancy
from tapchecker import optSelfCon
from tapchecker import optTACon
import random


def check(db, userId="", sceneId=0, adjusted=False):
    solver = Solver()
    apps = [[] for _ in range(3)]
    appletsList = list(cat.getAllRules(db, str(sceneId), userId))
    print(f"# rules = {len(appletsList)}")
    # appletsList = []
    # random sample
    # appletsList = random.choices(appletsListAll, k=500)

    appletsListLen = len(appletsList)
    for app in appletsList:
        apps[app[-1] - 1].append(app)
    appletsList = apps[sceneId]
    triggerdic = {}
    actiondic = {}
    length = len(appletsList)
    linkTable = [[False for _ in range(length)] for _ in range(length)]
    # 建立z3表达式的字典 不用每次都转换
    for i in range(length):
        triggers = appletsList[i][2]
        actions = appletsList[i][3]
        nums = triggers.split(",")
        for num in nums:
            exp = cat.conditionToZ3(cat.getCondition(num, db))
            if triggerdic.get(num) is None:
                triggerdic[num] = exp
        nums = actions.split(",")
        for num in nums:
            exp = cat.actionToZ3(cat.getAction(num, db))
            if actiondic.get(num) is None:
                actiondic[num] = exp
    # 添加系统策略
    policy = cat.getPolicy(db)
    # 添加环境影响
    # 建立链接表
    solver.push()
    effects = cat.getEffect(db)
    for e in effects:
        solver.append(e)
    for i in range(length):
        triggers = [triggerdic[num] for num in appletsList[i][2].split(",")]
        iTrigger = reduce(And, triggers)
        actions = [actiondic[num] for num in appletsList[i][3].split(",")]
        iAction = reduce(And, actions)
        for j in range(i + 1, length):
            triggers = [triggerdic[num] for num in appletsList[j][2].split(",")]
            jTrigger = reduce(And, triggers)
            actions = [actiondic[num] for num in appletsList[j][3].split(",")]
            jAction = reduce(And, actions)
            if solver.check((Implies(jTrigger, iAction))) == sat:
                linkTable[i][j] = True
            elif solver.check((Implies(iTrigger, jAction))) == sat:
                linkTable[j][i] = True
    for i in range(length):
        for j in range(length):
            for k in range(length):
                if i != j and linkTable[i][k] == True and linkTable[k][j] == True:
                    linkTable[i][j] = True
    solver.pop()

    start = time.time()
    if adjusted:
        res = optPolicyCon.f_adjusted(
            appletsList, triggerdic, actiondic, linkTable, policy
        )
    else:
        res = optPolicyCon.f(appletsList, triggerdic, actiondic, linkTable, policy)
    elapsed = time.time() - start

    return {"times": elapsed, "conflicts": res}
