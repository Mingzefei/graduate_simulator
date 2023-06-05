from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import random
import time


app = Flask(__name__)

@app.route('/')
def index():
    state = {'name': 'John', 'age': 30}
    return render_template('index.html', state=state)

if __name__ == '__main__':
    app.run(debug=True)
