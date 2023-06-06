from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import random
import time
from io import BytesIO
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt
from  markupsafe import Markup
import scienceplots
plt.style.use(['science','no-latex'])


app = Flask(__name__)


class Game:
    def __init__(self):
        # 事件
        self.round = 1
        self.event_id = 'f-1'
        self.is_in_stochastic_event = False
        self.next_stochastic_event = '' # 取用后清空
        # 数值面板
        self.san = 8 # 精神值
        self.wealth = 2 # 财富值
        self.energy = 8 # 精力值
        self.intimate = 0 # 亲密值
        self.academic = 0 # 学术值
        # 历史数据
        self.history = {
                'event_id' : [],
                'san' : [self.san],
                'wealth' : [self.wealth],
                'energy' : [self.energy],
                'intimate' : [self.intimate],
                'academic' : [self.academic]
                }
        # 结局（多个）
        self.endings = []
        # 事件库
        with open('../data/processed/events.json', 'r', encoding='utf-8') as f:
            events_data = json.load(f)
            events_lib = events_data['events']
        self.events_lib = events_lib
        # 结局库
        with open('../data/processed/endings.json', 'r', encoding='utf-8') as f:
            endings_data = json.load(f)
            endings_lib = endings_data['endings']
        self.endings_lib = endings_lib

    def set_random_seed(self, seed):
        # 设置随机种子
        self.seed = seed
        random.seed(self.seed)

    def record_history(self):
        # 记录历史数据
        self.history['event_id'].append(self.event_id)
        self.history['san'].append(self.san)
        self.history['wealth'].append(self.wealth)
        self.history['energy'].append(self.energy)
        self.history['intimate'].append(self.intimate)
        self.history['academic'].append(self.academic)

    def get_event(self):
        # 根据id获取当前事件
        for event in self.events_lib:
            if event['id'] == self.event_id:
                return event

    def update_dataframe(self, result):
        # 根据选项结果更新数值面板
        self.san += result['san']
        self.san = max(min(self.san, 10), -3)
        self.wealth += result['wealth']
        self.wealth = max(min(self.wealth, 20), -5)
        self.energy += result['energy']
        self.energy = max(min(self.energy, 10), 0)
        self.intimate += result['intimate']
        self.intimate = max(min(self.intimate, 10), 0)
        self.academic += result['academic']
        self.academic = max(min(self.academic, 10), 0)

    def get_random_event_id(self):
        has_found_event = False
        while not has_found_event:
            next_event = random.choice(self.events_lib)
            if next_event['the_previous_id']:
                continue
            if next_event['limit_time_range']:
                left_limit = next_event['limit_time_range'].split('-')[0]
                right_limit = next_event['limit_time_range'].split('-')[1]
                if left_limit in self.history['event_id'] and right_limit not in self.history['event_id']:
                    pass
                else:
                    continue
            has_found_event = True

        return next_event['id']

    def get_next_event(self, option):
        # 下一个事件，优先判定是否触发固定事件，其次随机关联事件，最后随机独立事件
        if self.round + 1 == 5:
            next_event_id = 'f-2' # 固定事件-确定方向
        elif self.round + 1 == 7:
            next_event_id = 'f-3' # 固定事件-研究生第一个暑假
        elif self.round + 1 == 10:
            next_event_id = 'f-4' # 固定事件-开题
        elif self.round + 1 == 15:
            next_event_id = 'f-5' # 固定事件-毕业
        elif self.next_stochastic_event: # 存在未使用的关联事件
            next_event_id = self.next_stochastic_event
            self.next_stochastic_event = '' # 使用后清空
        else:
            next_event_id = self.get_random_event_id()

        # 根据选项和是否有未取用的关联事件，更新 next_stochastic_event
        if not self.next_stochastic_event:
            self.next_stochastic_event = option['the_next_id']

        return next_event_id

    def is_reach_end(self):
        # 触发结局：已触发毕业且无随机关联事件
        if 'f-5' in self.history['event_id']:
            if not self.next_stochastic_event:
                return True
        return False

    def get_endings(self):
        # 根据数值面板获取结局
        the_endings = []

        count_low_san = len([x for x in self.history['san'] if x < 1])
        if count_low_san > len(self.history['san']) / 2:
            the_endings.append('e-2')

        count_health = len([x for x in self.history['energy'] if x > 5])
        if count_health > len(self.history['energy']) / 2:
            the_endings.append('e-3')

        count_wealth = len([x for x in self.history['wealth'] if x > 8])
        if count_wealth > len(self.history['wealth']) / 2:
            the_endings.append('e-4')

        if self.history['intimate'][-1] > 8:
            the_endings.append('e-5')

        if self.history['academic'][-1] > 8:
            the_endings.append('e-6')

        if len(the_endings) <= 1:
            the_endings.append('e-1')

        return the_endings

    def update_game(self, option):
        # 玩家做出选项
        result = option['result']
        # 更新数值面板
        self.update_dataframe(result)
        # 记录
        self.record_history()
        # 判断是否触发结局，更新事件
        if self.is_reach_end():
            self.endings = self.get_endings()
        else:
            self.event_id = self.get_next_event(option)
            self.round += 1
            self.energy += 3 # 增加体力

    def plot_history(self):
        # plot
        fig = plt.figure(figsize=(5,4))
        plt.plot(self.history['san'], label='SAN')
        plt.plot(self.history['wealth'], label='WEALTH')
        plt.plot(self.history['energy'], label='ENERGY')
        plt.plot(self.history['intimate'], label='INTIMACY')
        plt.plot(self.history['academic'], label='ACADEMIC')
        plt.legend()
        # Render fig as an image in memory
        output = BytesIO()
        FigureCanvas(fig).print_png(output)

        # Convert image to base64 encoded string
        image_data = base64.b64encode(output.getvalue()).decode('utf-8')
        return image_data


game = Game()
seed = None

@app.route("/", methods=["GET", "POST"])
def index():
    global seed
    if request.method == "POST":
        seed = request.form.get("seed")
        if not seed:
            seed = str(time.time())
        game.set_random_seed(seed)
        return redirect(url_for("play"))
    return render_template("index.html")

@app.route("/play", methods=["GET", "POST"])
def play():


    if seed is None:
        return redirect(url_for("index"))

    if request.method == "POST":
        option = request.form.get("option")
        option = eval(option)
        game.update_game(option)

    # 传递游戏状态，并转为 json 格式
    event = game.get_event()
    options = event['options']
    state = {
        "san": game.san,
        "wealth": game.wealth,
        "energy": game.energy,
        "intimate": game.intimate,
        "academic": game.academic,
        "event_description": event['description'],
        "options": options,
        "history": game.history,
        "endings": game.endings,
    }
    state = jsonify(state).json

    # 判定是否触发结局
    if game.endings:
        # endings
        endings = {}
        for ending in game.endings:
            # 从 game.endings_lib 中获取结局内容
            for e in game.endings_lib:
                if e['id'] == ending:
                    endings[e['description_short']] = e['description']
        endings = jsonify(endings).json
        return render_template("end.html", endings=endings, image_data=Markup(game.plot_history()))
    else:
        return render_template("play.html", state=state)

if __name__ == '__main__':
    app.run(debug=True)
