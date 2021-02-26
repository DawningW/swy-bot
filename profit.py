# coding=utf-8

from enum import Enum, auto
import math
import time
import pulp
import swy
from utils import timeToSecond, secondToTime

class Goals(Enum):
    """
    指定线性规划的目标函数

    MAX_MONEY 总利润最大
    MAX_TIME 总烹饪时间最长
    MAX_CONSUMPTION 消耗的食材最多
    ALL 小孩纸才做选择, 大人全都要
    """
    MAX_MONEY = 1
    MAX_TIME = auto() 
    MAX_CONSUMPTION = auto()
    ALL = auto()

def calculate(foods, materials, cooks, goal=Goals.MAX_MONEY):
    MIN_PRODUCTION = 0 # 菜肴最小烹饪量
    MAX_PRODUCTION = 30 # 菜肴最大烹饪量
    VAR_NUM = len(foods) # 变量个数
    consumptions = [] # 每种食材的消耗量
    # 决策变量
    # 各菜肴烹饪数量 x, y, z, ... (0 <= x, y, z, ... <= 30)
    variables = [pulp.LpVariable(str(i), MIN_PRODUCTION, MAX_PRODUCTION, pulp.LpInteger) for i in range(VAR_NUM)]
    # 各菜肴是否被烹饪(二值变量) x', y', z', ... (x', y', z' = 0 或 1)
    cook_status = [pulp.LpVariable(str(i) + "_status", cat=pulp.LpBinary) for i in range(VAR_NUM)]
    # 约束条件
    constraints = []
    # 每种食材消耗量不超过总量 V(x, y, z, ...) <= V总, M(x, y, z, ...) <= M总, ...
    for ingredient in swy.Ingredients:
        consumption = pulp.lpSum([foods[i].getConsumption(ingredient) * variables[i] for i in range(VAR_NUM)])
        consumptions.append(consumption)
        constraints.append(consumption <= materials[ingredient])
    # 确保菜肴的烹饪状态为1时烹饪数量才大于0 0 * x' <= x <= 30 * x'
    for i in range(VAR_NUM):
        constraints.append(variables[i] >= MIN_PRODUCTION * cook_status[i])
        constraints.append(variables[i] <= MAX_PRODUCTION * cook_status[i])
    # 最多只能有食魂数量个变量不为0 x' + y' + z' + ... <= 5
    constraints.append(pulp.lpSum(cook_status) <= len(cooks))
    # 目标函数
    # 总利润f(x, y, z, ...)=各菜肴烹饪数量乘以单价的总和x * P(x)+ y * P(y) + z * P(z) + ...
    obj_money = pulp.lpSum([foods[i].price * variables[i] for i in range(VAR_NUM)])
    # 总时间g(x, y, z, ...)=各菜肴烹饪数量乘以单个烹饪时间乘以食魂加成的总和
    obj_time = pulp.lpSum([foods[i].time * variables[i] for i in range(VAR_NUM)])
    # 总消耗食材h(x, y, z, ...)=各菜肴烹饪数量乘以消耗食材量的总和
    obj_consumption = pulp.lpSum(consumptions)
    # 加权 TODO 尝试其他将多目标线性规划转为单目标的方法?
    objective = obj_money / 15_0000 + obj_consumption / sum(materials)
    
    problem = pulp.LpProblem("swy_problem", pulp.LpMaximize)
    problem.addVariables(variables)
    problem.addVariables(cook_status)
    for constraint in constraints:
        problem.addConstraint(constraint)
    if goal == Goals.MAX_MONEY:
        problem.setObjective(obj_money)
    elif goal == Goals.MAX_TIME:
        problem.setObjective(obj_time)
    elif goal == Goals.MAX_CONSUMPTION:
        problem.setObjective(obj_consumption)
    elif goal == Goals.ALL:
        problem.setObjective(objective)
        print("目前混合模式采用加权把多目标转化为单目标函数, 效果不好")
    problem.solve()
    # pulp.LpStatus[problem.status]
    if problem.status != pulp.LpStatusOptimal:
        return None, 0, None

    mapping = sorted(enumerate(cooks), key=lambda x: x[1])
    temp = []
    for i, var in enumerate(variables):
        count = int(pulp.value(var))
        if count > 0:
            temp.append({
                "food": foods[i],
                "count": count,
                "time": foods[i].time * count
            })
    temp.sort(key=lambda x: x["time"], reverse=True)
    result = [None] * len(temp)
    for index, item in enumerate(temp):
        # TODO 游戏实际是把菜和食魂的百分比缩减加在一起的, 我写成乘法了
        item["time"] = math.ceil(item["time"] * mapping[index][1])
        result[mapping[index][0]] = item
    rest_materials = [material - int(pulp.value(exp)) for material, exp in zip(materials, consumptions)]
    return result, int(pulp.value(obj_money)), rest_materials

def run():
    # pulp.LpSolverDefault = pulp.COIN_CMD(path="./libs/cbc.exe")
    print("欢迎使用食物语线性规划做菜计算器")
    print("原作者ic30rs, 现由WC维护")
    foods = swy.readFoods()
    materials = []
    cooks = []
    print("请输入想要烹饪的菜肴的品质, 用空格分割, 不输入则默认使用全部菜肴")
    str = input("")
    if str != "":
        strs = str.split(' ')
        dishtypes = set([swy.Rarities(r) for r in strs])
        foods = [food for food in foods if food.rarity in dishtypes]
    print("请输入食材数量, 格式为: 菜 肉 谷 蛋 鱼 虾")
    str = input("")
    strs = str.split(' ')
    for i in range(len(swy.Ingredients)):
        materials.append(int(strs[i]) if i < len(strs) else 0)
    print("请输入食魂技能缩短烹饪时长的百分比, 用空格分割, 可不输入百分号")
    print("注: 无缩短请输入0, 根据您输入的项数来确定做菜的食魂数量")
    str = input("")
    strs = str.split(' ')
    for percent in strs:
        cooks.append(1 - int(percent) / 100)
    print("1. 最大贝币收益\n2. 最长烹饪时间\n3. 最多食材消耗\n4. 我全都要!")
    str = input("请输入目标函数种类的序号: ")
    if str == "":
        print("未输入, 默认使用最大贝币收益")
        str = "1"
    type = Goals(int(str))
    print("正在计算中, 请稍候...")
    t = time.time()
    result, totalmoney, restmaterials = calculate(foods, materials, cooks, type)
    print("计算完成, 耗时 %f 秒" % (time.time() - t))
    if result is None:
        print("很抱歉, 该问题无解或有无穷多个最优解")
        return
    print("结果为(按照输入的顺序):")
    for index, item in enumerate(result):
        cooktime = secondToTime(item["time"])
        money = item["food"].price * item["count"]
        print("%d. %sX%d 耗时: %s 盈利: %d贝币" % (index + 1, item["food"].name, item["count"], cooktime, money))
    print("总利润: %d贝币" % totalmoney)
    print("剩余食材: 菜%d 肉%d 谷%d 蛋%d 鱼%d 虾%d" % tuple(restmaterials))
    return

# 测试
if __name__ == "__main__":
    run()
