conda activate graduate_game

export FLASK_APP=app
export GAME_PATH=~/graduate_simulator/app
export RESULTS_PATH=~/graduate_simulator/results

alias run="python $GAME_PATH/app.py"
alias nrun="nohup python $GAME_PATH/app.py > $RESULTS_PATH/app.log 2>&1 &"
