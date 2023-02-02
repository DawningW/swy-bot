import cv2
from .task import Task, task
from algorithms.detect import isimagesame, findtemplate
from algorithms.matching import canConnect
from utils import readimage
try:
    from constant import *
except:
    # **若想使用请自行修改以下数据**
    # 消除的时间间隔
    TIME_INTERVAL = 1.0
    # 游戏区域距离屏幕左方的距离
    MARGIN_LEFT = 0
    # 游戏区域距离屏幕顶部的距离
    MARGIN_TOP = 0
    # 横向方块数量
    HORIZONTAL_NUM = 10
    # 纵向方块数量
    VERTICAL_NUM = 10
    # 方块宽度
    SQUARE_WIDTH = 100
    # 方块高度
    SQUARE_HEIGHT = 100
    # 切片处理时的左上和右下坐标
    SUB_LT_X = 20
    SUB_LT_Y = 20
    SUB_RB_X = 80
    SUB_RB_Y = 80

class MiniGameTask(Task):
    """活动小游戏挂机任务的基类"""

    def __init__(self, button_name):
        super().__init__()
        self.template_button = readimage(button_name)

    async def run(self, player):
        started = False
        timer = self.timer(3)
        while True:
            targets = findtemplate(self.frame, self.template_button)
            if not started:
                # 未点过开始按钮
                if targets:
                    # 找到开始按钮
                    x, y = targets[0]
                    player.click(x, y)
                    await self.wait(1)
                    started = True
                    timer = self.timer(2)
                    continue
                elif timer.timeout():
                    # 未找到开始按钮且超时
                    print("未找到开始按钮, 请确认您正位于小游戏界面")
                    return False
            else:
                # 已点过开始按钮
                if not targets:
                    # 未找到开始按钮
                    print("开始小游戏")
                    return True
                elif timer.timeout():
                    # 1秒后还能找到开始按钮
                    print("点击按钮后小游戏没有开始, 1秒后重试")
                    await self.wait(1)
                    started = False
                    timer = self.timer(3)
                    continue
            await self.next()

@task("自动小游戏-千人千面", "需自行修改代码进行配置")
class QianRenQianMianTask(MiniGameTask):
    """千人千面自动连连看"""

    def __init__(self):
        super().__init__("minigame_btn")

    async def run(self, player):
        if not await super().run(player):
            return
        # 图像切片并保存在数组中
        squares = []
        for j in range(VERTICAL_NUM):
            for i in range(HORIZONTAL_NUM):
                x = MARGIN_LEFT + i * SQUARE_WIDTH
                y = MARGIN_TOP + j * SQUARE_HEIGHT
                square = self.frame[y:(y + SQUARE_HEIGHT), x:(x + SQUARE_WIDTH)]
                # 每个方块向内缩小一部分防止边缘不一致造成干扰
                square = square[SUB_LT_Y:SUB_RB_Y, SUB_LT_X:SUB_RB_X]
                squares.append(square)
        # 相同的方块作为一种类型放在数组中
        types = []
        for square in squares:
            if self.isbackground(square):
                continue
            if next((type for type in types
                    if isimagesame(square, type)), None) is None:
                types.append(square)
        # 将切片处理后的图片数组转换成相对应的数字矩阵
        result = []
        num = 0
        for j in range(VERTICAL_NUM):
            line = []
            for i in range(HORIZONTAL_NUM):
                if self.isbackground(squares[num]):
                    line.append(0)
                else:
                    for t in range(len(types)):
                        if isimagesame(squares[num], types[t]):
                            line.append(t + 1)
                            break
                num += 1
            result.append(line)
        # 执行自动消除
        await self.next()
        while True:
            # 绘制网格
            # for j in range(VERTICAL_NUM):
            #     for i in range(HORIZONTAL_NUM):
            #         x = MARGIN_LEFT + i * SQUARE_WIDTH
            #         y = MARGIN_TOP + j * SQUARE_HEIGHT
            #         cv2.rectangle(self.frame, (x, y), (x + SQUARE_WIDTH, y + SQUARE_HEIGHT), (0, 255, 0), 1)
            # 执行消除算法
            pair = self.matchpair(result)
            if pair:
                ((x1, y1), (x2, y2)) = pair
                player.click(x1, y1)
                await self.wait(TIME_INTERVAL)
                player.click(x2, y2)
                await self.wait(TIME_INTERVAL)
            else:
                # TODO 判断一下出现结束画面才算完毕, 否则等待一会后重新规划
                print("自动消除运行完毕")
                break

    def matchpair(self, grid):
        # 定位第一个选中点
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j] != 0:
                    # 定位第二个选中点
                    for m in range(len(grid)):
                        for n in range(len(grid[0])):
                            if grid[m][n] != 0:
                                if canConnect(i, j, m, n, grid):
                                    # 消除成功
                                    grid[i][j] = 0
                                    grid[m][n] = 0
                                    x1 = MARGIN_LEFT + j * SQUARE_WIDTH
                                    y1 = MARGIN_TOP + i * SQUARE_HEIGHT
                                    x2 = MARGIN_LEFT + n * SQUARE_WIDTH
                                    y2 = MARGIN_TOP + m * SQUARE_HEIGHT
                                    return ((x1 + SQUARE_WIDTH / 2, y1 + SQUARE_HEIGHT / 2),
                                            (x2 + SQUARE_WIDTH / 2, y2 + SQUARE_HEIGHT / 2))
        return ()

    def isbackground(self, img):
        # TODO 是否有更好的算法?
        return abs(img[:, :, 0].mean() - 54) <= 10 and abs(img[:, :, 1].mean() - 70) <= 20 and abs(img[:, :, 2].mean() - 105) <= 15
