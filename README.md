# graduate simulator

研究生模拟器，一个基于 `flask` 框架的文本对话游戏，目的在于向玩家展示研究生的生存情况。

该项目为 2023 年 6 月 北京航空航天大学 《自然辩证法概论》 课程大作业，已部署在 [网址](http://43.143.145.165:5000/)，[备用网址](http://43.143.145.165:5001/)。

## 项目启用

### 环境配置

```bash
conda create -n graduate_game python=3.11
conda activate graduate_game
pip install -r requirements.txt
# clone 该仓库后，根据仓库具体位置添加如下变量
export FLASK_APP=app
export GAME_PATH=/path/to/app
export RESULTS_PATH=/path/to/results
```

### 运行

```bash
python $GAME_PATH/app.py
```

服务器后台运行：
```bash
nohup python $GAME_PATH/app.py > $RESULTS_PATH/app.log 2>&1 &
```

## 项目结构

```text
.
├── app
│   ├── app.py # 主程序
│   ├── font
│   │   └── simsun.ttc # 字体文件
│   └── templates # 模板文件
│       ├── end.html
│       ├── index.html
│       └── play.html
├── data
│   ├── processed
│   │   ├── endings.json # 结局
│   │   └── events.json # 事件
│   ├── raw
│   │   ├── 事件-汇总.xlsx # 事件汇总表
│   │   └── 事件-汇总-统一.xlsx # 事件汇总表，统一风格
│   └── template.json # 模板
├── docs
├── env.sh
├── LICENSE
├── README.md
├── requirements.txt
├── results
│   ├── app.log # 日志文件
│   └── app.csv # 结局记录
└── tools
    └── transform.py # 将 excel 文件转换为可用的 json 文件

```