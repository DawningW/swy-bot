from .player import addplayer, players
try:
    from .native import NativePlayer
    addplayer("原生模式", "需先启动安卓虚拟机并打开食物语", NativePlayer)
except ModuleNotFoundError as e:
    addplayer("原生模式", e.name, None)
try:
    from .adb import ADBPlayer
    addplayer("ADB模式", "需手机连接电脑开启调试模式并打开食物语", ADBPlayer)
except ModuleNotFoundError as e:
    addplayer("ADB模式", e.name, None)
try:
    from .scrcpy import ScrcpyPlayer
    addplayer("混合模式(*推荐*)", "使用scrcpy快速获取手机截屏并模拟点击", ScrcpyPlayer)
except ModuleNotFoundError as e:
    addplayer("混合模式", e.name, None)
from .debug import DebugPlayer
addplayer("调试模式", "读取程序目录下的test.png并进行图像识别", DebugPlayer)
