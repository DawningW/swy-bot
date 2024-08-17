# swy-bot
![swy-bot](https://socialify.git.ci/DawningW/swy-bot/image?description=1&forks=1&issues=1&language=1&logo=https%3A%2F%2Fgithub.com%2FDawningW%2Fswy-bot%2Fblob%2Fandroid%2Fapp%2Fsrc%2Fmain%2Fres%2Fmipmap-xxhdpi%2Fic_launcher.png%3Fraw%3Dtrue&name=1&owner=1&pattern=Floating%20Cogs&pulls=1&stargazers=1&theme=Auto)

~~由于食物语已于2024年6月18日停止运营, 本项目即日起进行归档, 停止维护, 少主们有缘再会! 如有需要, 本项目中包含的scrcpy客户端将移至独立仓库进行更新~~

**食物语·陪伴版已于2024年8月16日上线, 承诺永不关服, 因此本项目恢复维护, 但将进入长期支持状态, 仅修复bug, 随缘添加新功能**

> 百田和swy同寿

## 简介
食物语自动挂机脚本, 主要用于客潮和活动小游戏(目前仅包括千人千面自动消除)

由于某些原因小游戏自动挂机仅提供算法, 不提供配置, 请在tasks/minigame.py中自行修改配置

目前已支持Android系统原生运行脚本, 但有一些性能问题, 详情请见android分支, 若想体验可到releases中下载

现已加入食物语线性规划做菜计算器, 但处于早期测试阶段, 如遇bug请提交issue

---
## 食用方式
详见程序内指引

**注意:** 若使用ADB和Scrcpy模式, 请确保系统环境变量中有ADB, 并且ADB已连接至手机

---
## 食材
必需依赖:
- Python 3.8+
- numpy
- opencv-python

平台特定(现已引入动态加载模式, 未安装库仅会禁用对应模式, 脚本仍可正常运行):
- Windows原生模式:
    - pywin32
- linux和mac原生模式:
    - PyAutoGUI
- 任意系统ADB模式:
    - pure-python-adb
- 任意系统Scrcpy模式:
    - av

线性规划做菜计算器:
- PuLP

---
## 菜谱&改良
本项目可在Windows, Linux, MacOS和Android系统上运行, Android系统需要专用的用于加载脚本的APP才能运行, 详见android分支

另外本挂机脚本实际上提供了一个框架, 经过简单修改应该也能用于其他游戏, 甚至是用于训练人工智能玩游戏(逃

本项目欢迎各位空桑少主贡献代码

### 项目结构
- libs/ 脚本所需的库, 目前只有Scrcpy的服务端
- data/ 存储游戏数据和挂机所需资源的目录
- saved/ 截图会保存在这个目录
- algorithms/ 算法
    - detect.py 图像识别相关算法
    - matching.py 自动连连看算法(原作者TheThreeDog)
- players/ 模式
    - player.py 模式基类
    - native.py 通过原生窗口与游戏交互
    - adb.py 通过ADB与游戏交互
    - scrcpy.py 通过Scrcpy与游戏交互
    - debug.py 调试用
- tasks/ 挂机任务
    - task.py 挂机任务基类
    - kechao.py 客潮挂机任务
    - minigame.py 小游戏挂机任务
- platforms/ 工具模块的平台相关实现
    - console.py 具有命令行的系统上的实现
    - windows.py Windows系统相关实现
    - linux.py Linux系统相关实现
    - android.py Android系统相关实现
- main.py 主模块
- profit.py 线性规划做菜计算器(可单独运行)
- swy.py 食物语游戏数据(单独运行为输出游戏数据)
- scrcpy.py Python实现的Scrcpy客户端
- utils.py 工具模块

### 自动挂机
详见players和tasks目录

### 线性规划做菜计算器
线性规划算法详见profit.py中的注释

#### 关于烹饪时间缩短百分比
根据计算, 菜本身的缩减和食魂的生活技能提供的缩减是相加的关系

但源于我的疏忽, 脚本中的算法是相乘, 但是结果没差太多, 所以不改了(~~真不是懒~~)

另外烹饪时间出现小数的话只有入没有舍, 是ceil

### 自动小游戏
由于某些原因, 本项目仅提供用于学习的算法, 不包含配置, 如需使用请自行配置

---
## 如何烹饪
1. 拿走菜谱(克隆仓库到本地)
1. 准备好食材(安装第三方库)
1. 开始做菜(运行main.py)
1. 装盘(目前仍无法打包运行, 请考虑使用Android原生版本)
1. 随心所欲地修改菜谱(请随意修改代码)

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
2021/9/13 加入自动连连看算法, 初步支持Linux
2021/9/14 已加入对Linux和MacOS的支持, 但尚未测试, 更新版本号至V1.6
2021/9/17 已加入千人千面自动挂机功能, 更新版本号至V1.7
2023/2/2 代码重写, 用协程替代状态机, 实现动态加载模式, 移植到Android系统, 由于更新内容较多, 更新版本号为V2.0
2023/7/12 为适配Android12, 客潮截图现在保存在相册中, 而非Android/data, 更新版本号为V2.1
2023/9/8 更新Scrcpy至1.25, 修复Android版挂机脚本在鸿蒙系统上的一些问题, 更新版本号为V2.2
2023/9/9 适配Scrcpy 2.1.1, 更新版本号为V2.3
2024/6/20 项目归档, 感谢大家的支持
2024/8/17 复活吧我的爱人!
</pre>
</details>

---
## 厨师们
详见 [Contributors](https://github.com/DawningW/swy-bot/graphs/contributors)

---
## 特别致谢
所有第三方库的开发者

Scrcpy功能参考自:
- [py-scrcpy](https://github.com/Allong12/py-scrcpy)
- [naive-scrcpy-client](https://github.com/LostXine/naive-scrcpy-client)
- [android_autoclicker](https://github.com/JKookaburra/android_autoclicker)

线性规划做菜计算器参考自:
- [swy_profit](https://github.com/ic30rs/swy_profit)

自动连连看算法来自:
- [Auto-Lianliankan](https://github.com/TheThreeDog/Auto-Lianliankan)

感谢以上项目的开发者

以及这篇Python线性规划库PuLP教程: [PuLP简介](https://fancyerii.github.io/2020/04/18/pulp/)

---
## 版权信息
本项目以MIT协议开源, 引用的代码仍按照原协议开源

仅供学习交流, 严禁用于盈利

使用本脚本造成的一切后果由使用者自行承担
