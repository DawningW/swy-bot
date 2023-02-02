import random
import math
import time
import cv2
from .task import RepeatTask, task
from algorithms.detect import findtemplate, findcircle
from utils import readimage, writeimage

@task("自动客潮", "请将界面停留在餐厅")
class KeChaoTask(RepeatTask):
    """客潮自动化"""

    def __init__(self):
        self.template_button = readimage("kechao_btn")
        self.template_dish = readimage("kechao_dish_part")
        self.template_title = readimage("kechao_title_part")

    async def runonce(self, player):
        while True:
            restart = False
            # 餐厅界面
            timer = self.timer(3)
            while True:
                # 寻找客潮按钮
                target = next(((x, y) for x, y in findcircle(self.frame, 25)
                        if x > (self.frame.shape[1] * 0.9) and y < (self.frame.shape[0] * 0.2)), None)
                if target is not None:
                    # 找到客潮按钮
                    x, y = target
                    player.clickaround(x, y)
                    await self.wait(1)
                    break
                elif timer.timeout():
                    # 未找到客潮按钮且超时
                    print("未找到客潮按钮, 请确认您正位于餐厅界面")
                    return False
                await self.next()
            # 客潮对话框
            clicked = False
            timer = self.timer(2)
            while True:
                # 寻找开始按钮
                targets = findtemplate(self.frame, self.template_button)
                if not clicked:
                    # 未点过开始按钮
                    if targets:
                        # 找到开始按钮
                        x, y = targets[0]
                        player.clickaround(x, y)
                        await self.wait(2)
                        clicked = True
                        timer = self.timer(2)
                        continue
                    elif timer.timeout():
                        # 2秒后还未找到开始按钮, 回退到餐厅界面
                        print("未找到客潮对话框, 回退到餐厅界面重试")
                        restart = True
                        break
                else:
                    # 已点过开始按钮
                    if not targets:
                        # 未找到开始按钮, 进入客潮
                        print("进入客潮")
                        await self.wait(2)
                        break
                    elif timer.timeout():
                        # 2秒后还能找到开始按钮, 结束任务
                        print("点击按钮后没有开始, 可能是客潮开启次数不足")
                        return False
                await self.next()
            if not restart:
                break
        # 客潮挂机中
        point_cache = []
        timer = self.timer(15)
        while True:
            # 处理点的缓存
            point_cache = [(x, y, t - 1) for x, y, t in point_cache if t > 1]
            # 识别圆来寻找菜(旧版本用模版匹配, 效果不好)
            end = False
            targets = []
            for x, y in findcircle(self.frame, 25):
                if x > (self.frame.shape[1] * 0.9):
                    continue
                if y > (self.frame.shape[0] * 0.8):
                    end = True
                    break
                cv2.circle(self.frame, (x, y), 25, (0, 0, 255), 3)
                if next(((cx, cy) for cx, cy, _ in point_cache
                        if math.dist((x, y), (cx, cy)) < 5), None) is None:
                    targets.append((x, y))
            if end:
                # 客潮结束回到餐厅
                print("客潮结束")
                await self.wait(2)
                break
            elif targets:
                # 随机挑选一个客人上菜!
                x, y = random.choice(targets)
                player.clickaround(x, y)
                point_cache.append((x, y, 10))
                timer = self.timer(15)
            elif timer.timeout():
                # 没人点菜, 停止挂机?
                print("超过15秒钟没有客人点菜了, 停止挂机")
                return False
            await self.next()
        # 客潮结算界面
        timer = self.timer(3)
        while True:
            # 寻找客潮结算界面
            targets = findtemplate(self.frame, self.template_title)
            if targets:
                # 正位于客潮结算界面
                x, y = targets[0]
                filename = "KeChao_" + time.strftime("%Y-%m-%d-%H-%M-%S")
                writeimage(filename, self.frame)
                print(f"已将客潮结算界面截图保存至: saved/{filename}.png")
                player.clickaround(x, y)
                await self.wait(2)
                break
            elif timer.timeout():
                # 未找到客潮结算界面
                print("未在3秒内进入客潮结算, 停止挂机")
                return False
            await self.next()
        return True
