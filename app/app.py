from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import json
import random
import time
from io import BytesIO
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt
from markupsafe import Markup
import csv
from datetime import timedelta
import os
import scienceplots
plt.style.use(['science', 'no-latex'])


app = Flask(__name__)
app.secret_key = 'kdjklfjkd87384hjdhjh'
app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)


class Game:
    def __init__(self):
        """
        This is a Python class constructor that initializes various attributes for a game, including event
        and ending libraries, historical data, and numerical values for the game's character.
        """
        # 事件
        self.round = 1
        self.event_id = 'f-1'
        self.is_in_stochastic_event = False
        self.next_stochastic_event = ''  # 取用后清空
        # 数值面板
        self.san = 8  # 精神值
        self.wealth = 2  # 财富值
        self.energy = 8  # 精力值
        self.intimate = 0  # 亲密值
        self.academic = 0  # 学术值
        # 历史数据
        self.history = {
            'event_id': [],
            'san': [self.san],
            'wealth': [self.wealth],
            'energy': [self.energy],
            'intimate': [self.intimate],
            'academic': [self.academic]
        }
        # 结局（多个）
        self.endings = []
        # 事件库
        with open('./data/processed/events.json', 'r', encoding='utf-8') as f:
            events_data = json.load(f)
            events_lib = events_data['events']
        self.events_lib = events_lib
        # 结局库
        with open('./data/processed/endings.json', 'r', encoding='utf-8') as f:
            endings_data = json.load(f)
            endings_lib = endings_data['endings']
        self.endings_lib = endings_lib

    def set_random_seed(self, seed):
        """
        This function sets a random seed for generating random numbers in Python.

        Args:
          seed: The seed parameter is an integer value that is used to initialize the random number
        generator. By setting a specific seed value, we can ensure that the sequence of random numbers
        generated by the program is the same every time it is run with the same seed value. This can be
        useful for testing and debugging purposes
        """
        # 设置随机种子
        self.seed = seed
        random.seed(self.seed)

    def record_history(self):
        """
        This function records historical data for various attributes of an event.
        """
        # 记录历史数据
        self.history['event_id'].append(self.event_id)
        self.history['san'].append(self.san)
        self.history['wealth'].append(self.wealth)
        self.history['energy'].append(self.energy)
        self.history['intimate'].append(self.intimate)
        self.history['academic'].append(self.academic)

    def get_event(self):
        """
        This function retrieves the current event from a list of events based on its ID.

        Returns:
          the event that matches the current event ID in the events library.
        """
        # 根据id获取当前事件
        for event in self.events_lib:
            if event['id'] == self.event_id:
                return event

    def update_dataframe(self, result):
        """
        This function updates a dataframe based on the results of a selected option.

        Args:
          result: The parameter "result" is a dictionary that contains the results of a user's choice in a
        game or simulation. The keys in the dictionary represent different attributes such as "san"
        (sanity), "wealth", "energy", "intimate" (intimacy), and "academic". The
        """
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
        """
        This function returns a random event ID from a list of events based on certain conditions.

        Returns:
          the ID of a randomly selected event from the events library, which meets certain conditions.
        """
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
        """
        This function determines the next event to occur in a game, prioritizing fixed events and then
        selecting from random associated or independent events.

        Args:
          option: There is no parameter named "option" in the given code snippet. Therefore, it is not
        possible to determine what this parameter is without additional context or code.
        """
        # 下一个事件，优先判定是否触发固定事件，其次随机关联事件，最后随机独立事件
        if self.round + 1 == 5:
            next_event_id = 'f-2'  # 固定事件-确定方向
        elif self.round + 1 == 7:
            next_event_id = 'f-3'  # 固定事件-研究生第一个暑假
        elif self.round + 1 == 10:
            next_event_id = 'f-4'  # 固定事件-开题
        elif self.round + 1 == 15:
            next_event_id = 'f-5'  # 固定事件-毕业
        elif self.next_stochastic_event:  # 存在未使用的关联事件
            next_event_id = self.next_stochastic_event
            self.next_stochastic_event = ''  # 使用后清空
        else:
            next_event_id = self.get_random_event_id()

        # 根据选项和是否有未取用的关联事件，更新 next_stochastic_event
        if not self.next_stochastic_event:
            self.next_stochastic_event = option['the_next_id']

        return next_event_id

    def is_reach_end(self):
        """
        This function checks if the game has reached its end by verifying if a specific event has been
        triggered and there are no more random events left.

        Returns:
          The function `is_reach_end` returns a boolean value. It returns `True` if the condition of having
        triggered the graduation event and having no next stochastic event is met, and `False` otherwise.
        """
        # 触发结局：已触发毕业且无随机关联事件
        if 'f-5' in self.history['event_id']:
            if not self.next_stochastic_event:
                return True
        return False

    def get_endings(self):
        """
        This function returns a list of possible endings based on the values in the history dictionary.

        Returns:
          The function `get_endings` returns a list of strings representing the possible endings based on
        the player's history of `san`, `energy`, `wealth`, `intimate`, and `academic` values. The list may
        contain one or more endings.
        """
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
        """
        The function updates the game state by processing the player's option, updating the data panel,
        recording the history, and determining whether to trigger an ending or update the event.

        Args:
          option: The "option" parameter is a dictionary that contains the player's chosen option and its
        result. It is passed as an argument to the "update_game" method. The "result" key in the dictionary
        contains the numerical value that will be used to update the game's data panel.
        """
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
            self.energy += 3  # 增加体力

    def plot_history(self):
        """
        This function plots the history of various attributes and returns the plot as a base64 encoded
        string.

        Returns:
          a base64 encoded string of a plot that shows the history of the values of 'san', 'wealth',
        'energy', 'intimate', and 'academic' over time.
        """
        # plot
        fig = plt.figure(figsize=(5, 4))
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

    def reset(self):
        """
        The function `reset` re-initializes an object by calling its `__init__` method.
        """
        self.__init__()


def obj2dict(obj):
    """
    The function converts an object into a dictionary and removes two specific keys before returning the
    dictionary.

    Args:
      obj: The input parameter "obj" is an object that needs to be converted into a dictionary.

    Returns:
      The function `obj2dict` returns a dictionary containing the attributes and their values of the
    input object, except for the attributes named "events_lib" and "endings_lib" which are deleted from
    the dictionary before it is returned.
    """
    pr = {}
    for name in dir(obj):
        value = getattr(obj, name)
        if not name.startswith('__') and not callable(value):
            pr[name] = value
    # 删除其中的 events_lib 和 endings_lib
    del pr['events_lib']
    del pr['endings_lib']
    return pr


seed = None


@app.route("/", methods=["GET", "POST"])
def index():

    global seed

    # 读取 seed，跳转到 play 页面
    if request.method == "POST":
        seed = request.form.get("seed")
        if not seed:
            seed = str(time.time())
        game = Game()
        game.set_random_seed(seed)
        session['game'] = obj2dict(game)
        return redirect(url_for("play"))
    return render_template("index.html")


@app.route("/play", methods=["GET", "POST"])
def play():

    if "game" not in session:
        return redirect(url_for("index"))

    if seed is None:
        return redirect(url_for("index"))

    # 更新游戏
    game_dict = session['game']
    game = Game()
    game.__dict__.update(game_dict)
    if request.method == "POST":
        option = request.form.get("option")
        option = eval(option)
        game.update_game(option)

    session['game'] = obj2dict(game)
    # 传递游戏状态，json 格式
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
        return redirect(url_for("end"))
    else:
        return render_template("play.html", state=state)


@app.route("/end", methods=["GET", "POST"])
def end():

    if "game" not in session:
        return redirect(url_for("index"))

    # 重置游戏
    global seed
    game_dict = session['game']
    game = Game()
    game.__dict__.update(game_dict)
    if request.method == "POST":
        seed = None
        # game.reset()
        session.pop('game')
        return redirect(url_for("index"))

    # 输出结局
    endings = {}
    for ending in game.endings:
        # 从 game.endings_lib 中获取结局内容
        for e in game.endings_lib:
            if e['id'] == ending:
                endings[e['description_short']] = e['description']
    endings = jsonify(endings).json
    print(game.history)
    with open('./results/app.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([seed, game.history])
    return render_template("end.html", endings=endings, image_data=Markup(game.plot_history()))


if __name__ == '__main__':
    # app.run(host='10.0.24.9', port=5000)
    app.run(debug=True)
