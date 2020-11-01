import random
import json
from flask import Flask, render_template
from werkzeug import redirect
from src.chess import WHITE, BLACK, Board
from collections import deque

games = {}
""" :type: dict[str, (Board, int)] """
invites = {}
""" :type: dict[str, str] """
stranger_invites = deque()
""" :type: deque[str]"""
stranger_invites_color = None
""" :type: Optional[int] """

app = Flask(__name__)


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/game/<game_id>')
def game(game_id):
    try:
        board, player_color = games[game_id]
    except KeyError:
        return render_template('error.html')
    return render_template('game.html', board=board, player=player_color,
                           can_move=player_color == board.current_player_color())


def _create_id():
    return ''.join((random.choice('abc''def''ghi''jkl''mno''pqr''stu''vwx''yz') for _ in range(11)))


def create_id(d, v):
    id = _create_id()
    while id in d:
        id = _create_id()
    d[id] = v
    return id


def create_game():
    board = Board()
    return create_id(games, (board, WHITE)), create_id(games, (board, BLACK))


@app.route('/invite')
def invite():
    white_id, black_id = create_game()
    invite_id = create_id(invites, black_id)
    return render_template('invite.html', invite_id=invite_id, game_id=white_id)


@app.route('/join/<invite_id>')
def join(invite_id):
    try:
        return redirect(f'/game/{invites.pop(invite_id)}')
    except KeyError:
        return render_template('error.html')


def main():
    board = Board()


if __name__ == "__main__":
    main()
