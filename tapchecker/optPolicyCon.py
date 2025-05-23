# -*- coding:utf-8 -*-
from z3 import *
import pymysql
from tapchecker import connectAndTransfer as cat
import time
import ast
from functools import reduce


# 单独校验的时候用此函数，全部校验统一用f()
def policyCon(db, userId=""):
    solver = Solver()
    triggerdic = {}
    actiondic = {}
    appletsList = list(cat.getAllRules(db, userId))
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
    # 建立链接表
    solver.push()
    effects = cat.getEffect(db)
    for e in effects:
        solver.append(e)
    # print(solver)
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
            # print(Implies(jTrigger,iAction))
            # print(Implies(iTrigger,jAction))
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
    policy = cat.getPolicy(db)
    # 检验
    return f(appletsList, triggerdic, actiondic, linkTable, policy)


def f_adjusted(appletsList, triggerdic, actiondic, linkTable, policy):
    s = time.time()
    solver = Solver()
    pSolver = Solver()
    for p in policy:
        pSolver.append(p)
    # solver.set(unsat_core=True)
    # solver.assert_and_track(policy,'p')
    # print(pSolver,appletsList,linkTable)
    res = []
    length = len(appletsList)
    for i in range(length):
        triggers = [triggerdic[num] for num in appletsList[i][2].split(",")]
        iTrigger = reduce(And, triggers)
        actions = [actiondic[num] for num in appletsList[i][3].split(",")]
        iAction = reduce(And, actions)
        if (
            solver.check(And(True, iAction)) == sat
            and pSolver.check(And(True, iAction)) == unsat
        ):
            res.append(tuple([appletsList[i][0]]))
            continue

        for j in range(length):
            if i == j:
                continue
            triggers = [triggerdic[num] for num in appletsList[j][2].split(",")]
            jTrigger = reduce(And, triggers)
            actions = [actiondic[num] for num in appletsList[j][3].split(",")]
            jAction = reduce(And, actions)
            if (
                solver.check(And(iAction, jAction)) == sat
                and pSolver.check(And(iAction, jAction)) == unsat
            ):
                res.append(tuple(sorted((appletsList[i][0], appletsList[j][0]))))

            # if linkTable[i][j] == False:
            #     continue
            # if (
            #     solver.check(And(True, jAction)) == sat
            #     and pSolver.check(And(True, jAction)) == unsat
            # ):
            #     res.append(
            #         f"{appletsList[i][0]},{appletsList[j][0]},first-pairwise-conflict"
            #     )

    return res


def f_triple(appletsList, triggerdic, actiondic, linkTable, policy):
    s = time.time()
    solver = Solver()
    pSolver = Solver()
    for p in policy:
        pSolver.append(p)
    res = []
    length = len(appletsList)
    for i in range(length):
        triggers = [triggerdic[num] for num in appletsList[i][2].split(",")]
        iTrigger = reduce(And, triggers)
        actions = [actiondic[num] for num in appletsList[i][3].split(",")]
        iAction = reduce(And, actions)
        if (
            solver.check(And(True, iAction)) == sat
            and pSolver.check(And(True, iAction)) == unsat
        ):
            res.append(tuple((appletsList[i][0])))
            continue

        for j in range(length):
            if i == j:
                continue
            triggers = [triggerdic[num] for num in appletsList[j][2].split(",")]
            jTrigger = reduce(And, triggers)
            actions = [actiondic[num] for num in appletsList[j][3].split(",")]
            jAction = reduce(And, actions)
            if (
                solver.check(And(iAction, jAction)) == sat
                and pSolver.check(And(iAction, jAction)) == unsat
            ):
                res.append(tuple((appletsList[i][0], appletsList[j][0])))

            for k in range(length):
                if i == k or j == k:
                    continue
                triggers = [triggerdic[num] for num in appletsList[k][2].split(",")]
                kTrigger = reduce(And, triggers)
                actions = [actiondic[num] for num in appletsList[k][3].split(",")]
                kAction = reduce(And, actions)
                if (
                    solver.check(And(iAction, jAction, kAction)) == sat
                    and pSolver.check(And(iAction, jAction, kAction)) == unsat
                ):
                    res.append(
                        tuple(
                            (
                                appletsList[i][0],
                                appletsList[j][0],
                                appletsList[k][0],
                            )
                        )
                    )

    return res


def f(appletsList, triggerdic, actiondic, linkTable, policy):
    s = time.time()
    solver = Solver()
    pSolver = Solver()
    for p in policy:
        pSolver.append(p)
    # solver.set(unsat_core=True)
    # solver.assert_and_track(policy,'p')
    # print(pSolver,appletsList,linkTable)
    res = set()
    length = len(appletsList)
    for i in range(length):
        triggers = [triggerdic[num] for num in appletsList[i][2].split(",")]
        iTrigger = reduce(And, triggers)
        actions = [actiondic[num] for num in appletsList[i][3].split(",")]
        iAction = reduce(And, actions)
        if (
            solver.check(And(iTrigger, iAction)) == sat
            and pSolver.check(And(iTrigger, iAction)) == unsat
        ):
            res.add(tuple([appletsList[i][0]]))
            continue

        for j in range(length):
            if i == j:
                continue
            triggers = [triggerdic[num] for num in appletsList[j][2].split(",")]
            jTrigger = reduce(And, triggers)
            actions = [actiondic[num] for num in appletsList[j][3].split(",")]
            jAction = reduce(And, actions)
            if (
                (solver.check(And(iTrigger, jTrigger)) == sat or linkTable[i][j])
                and solver.check(And(iAction, jAction)) == sat
                and pSolver.check(And(iAction, jAction)) == unsat
            ):
                res.add(tuple(sorted((appletsList[i][0], appletsList[j][0]))))

            if linkTable[i][j] == False:
                continue
            if (
                solver.check(And(iTrigger, jAction)) == sat
                and pSolver.check(And(iTrigger, jAction)) == unsat
            ):
                res.add(tuple(sorted((appletsList[i][0], appletsList[j][0]))))

    return res
