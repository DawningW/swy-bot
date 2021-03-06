# swy-bot
# 食物语自动挂机脚本

## 简介
食物语自动挂机脚本, 主要用于客潮~~和活动小游戏~~(太难做砍掉了绝对不是因为我懒啊啊啊啊啊啊)

现已加入食物语线性规划做菜计算器, 但处于早期测试阶段, 如遇bug请提交issue

祝各位少主都能把喜欢的菜男人抱回家!
![双御.png](https://i.loli.net/2021/03/03/SpvI6GisAyPa8Dg.png)

<!-- **空桑好, 策划爬** -->

---
## 食用方式
详见程序内指引

**注意:** 若使用ADB(Scrcpy模式), 请确保系统环境变量中有ADB, 并且ADB已连接至手机

---
## 食材
- Python3
- opencv-python
- PyAV
- pywin32(仅限Windows)
- PyAutoGUI(Windows上不需要)
- pure-python-adb
- PuLP
- pyinstaller(如需要打包)

详见requirements.txt

---
## 菜谱&改良
目前本项目仅能在Windows上运行, 但经过简单修改就能在mac和linux上运行(~~不过我懒~~

另外本挂机脚本实际上提供了一个框架, 经过简单修改应该也能用于其他游戏, 甚至是用于训练人工智能玩游戏(逃

本项目欢迎各位空桑少主贡献代码

### 项目结构
- libs/ 脚本所需的库, 目前只有Scrcpy的服务端
- data/ 存储游戏数据和挂机所需资源的目录
- saved/ 截图会保存在这个目录
- main.py 主文件
- player.py 负责与游戏交互(通过原生窗口/ADB/Scrcpy)
- task.py 执行挂机任务
- windows.py 与Windows交互
- utils.py 工具模块
- swy.py 负责加载游戏数据
- profit.py 线性规划做菜计算器

### 自动挂机
详见player.py和task.py

### 线性规划做菜计算器
线性规划算法详见profit.py中的注释

#### 关于烹饪时间缩短百分比
根据计算, 菜本身的缩减和食魂的生活技能提供的缩减是相加的关系

但源于我的疏忽, 脚本中的算法是相乘, 但是结果没差太多, 所以不改了(~~真不是懒~~)

另外烹饪时间出现小数的话只有入没有舍, 是ceil

---
## 烹饪
1. 克隆仓库到本地
1. 准备好食材
1. 运行main.py
1. 如需构建, 请使用pyinstaller
1. 随心所欲地修改菜谱

---
## 烹饪日记
<details>
<summary>展开查看</summary>
<pre>
2020/10/27 项目开始开发
2020/11/3 实现ADB模式
2020/11/5 实现Windows原生模式
2020/12/5 客潮挂机从模板匹配改为识别圆
2021/2/1 大规模重构代码, 增加挂机任务类, 增加使用Scrcpy的模式(未完成), 更新版本号至V1.2
2021/2/21 使用装饰器注册挂机任务, 完成Scrcpy模式, 更新版本号至V1.3
2021/2/23 重做客潮挂机任务, 更新版本号至V1.4
2021/2/25 新增swy.py用于加载游戏数据, 初步实现线性规划做菜计算器
2021/2/26 更新菜肴数据为计算缩减后的烹饪时间, 更新版本号至V1.5
</pre>
</details>

---
## 厨师
详见CONTRIBUTOR.md

---
## 特别致谢
所有第三方库的开发者

Scrcpy功能参考自:
- [py-scrcpy](https://github.com/Allong12/py-scrcpy)
- [naive-scrcpy-client](https://github.com/LostXine/naive-scrcpy-client)
- [android_autoclicker](https://github.com/JKookaburra/android_autoclicker)

线性规划做菜计算器参考自:
- [swy_profit](https://github.com/ic30rs/swy_profit)

感谢以上项目的开发者

以及这篇Python线性规划库PuLP教程: [PuLP简介](https://fancyerii.github.io/2020/04/18/pulp/)

---
## 版权信息
本项目以MIT协议开源

仅供学习交流, 严禁用于盈利

使用本脚本造成的一切后果由使用者自行承担
