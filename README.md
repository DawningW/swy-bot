# swy-bot
# 食物语自动挂机脚本

## 简介
食物语自动挂机脚本, 主要用于客潮~~和活动小游戏~~(太难做砍掉了绝对不是因为我懒啊啊啊啊啊啊)

有计划加入食物语做菜优化, 引用[此项目](https://github.com/ic30rs/swy_profit)

PS: 每次做菜都剩下一大堆食材好烦啊

PSS: 那个活动的跑酷恶心死我了啊啊啊啊

**空桑好, 策划爬**

## 食用方式
详见程序内指引

**注意:** 若使用ADB(Scrcpy模式), 请确保系统环境变量中有ADB, 并且ADB已连接至手机

## 改良菜谱
目前本项目仅能在Windows上运行, 但经过简单修改就能在mac和linux上运行(~~不过我懒~~

另外本挂机脚本实际上提供了一个框架, 经过简单修改应该也能用于其他游戏, 甚至是用于训练人工智能玩游戏(逃

本项目欢迎各位空桑少主贡献代码

## 食材
- opencv-python
- PyAV
- pywin32(仅限Windows)
- PyAutoGUI(Windows上不需要)
- pure-python-adb
- pyinstaller(如需要打包)

详见requirements.txt

## 烹饪日记
2020/10/27 项目开始开发

2020/11/3 实现ADB模式

2020/11/5 实现Windows原生模式

2020/12/5 客潮挂机从模板匹配改为识别圆

2021/2/1 大规模重构代码, 增加挂机任务类, 增加使用Scrcpy的模式(未完成), 更新版本号至V1.2

2021/2/21 使用装饰器注册挂机任务, 完成Scrcpy模式, 更新版本号至V1.3

2021/2/23 重做客潮挂机任务, 更新版本号至V1.4

## 厨师
详见CONTRIBUTOR.md

## 特别致谢
所有第三方库的开发者

Scrcpy功能参考自:
- [py-scrcpy](https://github.com/Allong12/py-scrcpy)
- [naive-scrcpy-client](https://github.com/LostXine/naive-scrcpy-client)
- [android_autoclicker](https://github.com/JKookaburra/android_autoclicker)

感谢以上项目的开发者

## 版权信息
本项目以MIT协议开源

仅供学习交流, 严禁用于盈利

使用本脚本造成的一切后果由使用者自行承担
