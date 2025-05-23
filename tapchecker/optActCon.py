# -*- coding:utf-8 -*-
from z3 import *
import connectAndTransfer as cat
import pymysql
import time
from functools import reduce


def actionCon(db):
    triggerdic = {}
    actiondic = {}
    appletsList = list(cat.getAllRules(db, userId=""))[:100]
    length = len(appletsList)
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
    # 检验
    return f(appletsList, triggerdic, actiondic)


def f(appletsList, triggerdic, actiondic):
    s = time.time()
    aSolver = Solver()
    tSolver = Solver()
    res = []
    length = len(appletsList)
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

            tSolver.push()
            tSolver.add(iTrigger)
            tSolver.add(jTrigger)
            aSolver.push()
            aSolver.add(iAction)
            aSolver.add(jAction)

            if tSolver.check() == sat and aSolver.check() == unsat:
                # res = res if res != [] else [1]
                res.append((appletsList[i][1] + " ,and, " + appletsList[j][1]))
            tSolver.pop()
            aSolver.pop()
    # print(time.time()-s)
    # print(res)
    # res = [0] if res == [] else res
    return res

