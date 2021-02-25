# coding=utf-8

from enum import Enum, IntEnum, auto
from utils import timeToSecond, secondToTime

class Rarities(Enum):
    """稀有度"""
    UNKNOWN = "?" # 调料
    GOOD = "良" # 良品(N)
    NOBLE = "尚" # 尚品(R)
    TREASURE = "珍" # 珍品(SR)
    ROYAL = "御" # 御品(SSR)
    HOLY = "圣" # 圣品(SP)

class Ingredients(IntEnum):
    """食材"""
    VEGETABLE = 0
    MEAT = auto()
    GRAIN = auto()
    EGG = auto()
    FISH = auto()
    SHRIMP = auto()

class Food:
    def __init__(self, name, rarity, price, time, consumptions):
        self.name = name
        self.rarity = rarity
        self.price = price
        self.time = time
        self.consumptions = consumptions
        return

    def getConsumption(self, ingredient: Ingredients) -> int:
        """获取该菜肴所需的某种食材的数量"""
        return self.consumptions[ingredient]

foods = None

def readFoods() -> list:
    global foods
    if foods is None:
        foods = list()
        with open('./data/cuisine.csv', 'r', encoding='utf-8') as file:
            for line in file.readlines()[1:]:
                values = line.strip().split(',')
                name = values[0]
                rarity = Rarities(values[1])
                price = int(values[2])
                time = timeToSecond(values[3])
                consumptions = [int(values[i + 4]) for i in range(len(Ingredients))]
                foods.append(Food(name, rarity, price, time, consumptions))
    return foods

# 测试
if __name__ == "__main__":
    print("读取菜单")
    readFoods()
    for food in foods:
        print("%s(%s)   \t售价: %d  \t烹饪时间: %s(%d秒)  \t消耗食材: %s" % (food.name, food.rarity.value, food.price, secondToTime(food.time), food.time, str(food.consumptions)))
