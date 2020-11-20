import random

from src.shared import random_string
from datetime import datetime

from flask import Flask, render_template
from werkzeug.utils import redirect
from src.chess import WHITE, BLACK, opponent, Board
from collections import deque

games = {}
""" :type: dict[str, (Board, int)] """
invites = {}
""" :type: dict[str, str] """
stranger_invite = None

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
    can_move = player_color is None or player_color == board.current_player_color()
    td = datetime.now() - board.last_move_time
    return render_template('game.html', chr=chr, ord=ord, board=board, player=player_color,
                           can_move=can_move, chat=player_color is not None,
                           time=int((td.days * 24 * 60 * 60 + td.seconds) * 1000))


@app.route('/game/<game_id>/move/<move_desc>')
def move(game_id, move_desc):
    board, player_color = games[game_id]
    player_color = player_color or board.current_player_color()
    if player_color == board.current_player_color():
        try:
            if ';' in move_desc:
                r, c = map(int, move_desc.split(';'))
                board.move_f(r, c)
            else:
                r, c = board.promote_row, board.promote_col
                board.promote(int(move_desc))
            board.log_file.write(f"{datetime.now()} "
                                 f"{'White' if player_color == WHITE else BLACK} "
                                 f"move: {board.char_at(r, c)}{move_desc}\n")
        except (ValueError, IndexError):
            pass
    return redirect(f'/game/{game_id}')


@app.route('/game/<game_id>/post/<path:message>')
def post(game_id, message):
    board, player_color = games[game_id]
    board.chat.append(
        message.translate({ord(c[0]): f'&{c[1:]};' for c in ('&amp',
                                                             '<lt',
                                                             '“ldq''uo',
                                                             '”rdq''uo')}))
    board.log_file.write(f"{datetime.now()} "
                         f"{'White' if player_color == WHITE else BLACK} "
                         f"chat message: {message!r}")
    return redirect(f'/game/{game_id}')


# debug
@app.route('/game/<game_id>/fill-chat')
def fill_chat(game_id):
    games[game_id][0].chat.extend(['filler'] * 50)
    return redirect(f'/game/{game_id}')


def create_id(d, v):
    vid = random_string()
    while vid in d:
        vid = random_string()
    d[vid] = v
    return vid


def create_game():
    board = Board()
    white_id, black_id = create_id(games, (board, WHITE)), create_id(games, (board, BLACK))
    board.log_file.write(f'Start time: {datetime.now()}\n'
                         f'White ID: {white_id}\n'
                         f'Black ID: {black_id}\n')
    return white_id, black_id


@app.route('/play-with-self')
def play_with_self():
    board = Board()
    player_id = create_id(games, (board, None))
    board.log_file.write(f'Start time: {datetime.now()}\n'
                         f'Player ID: {player_id}')
    return redirect(f'/game/{player_id}')


@app.route('/play-with-friend')
def play_with_friend():
    return render_template('play_with_friend.html')


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


@app.route('/random_player')
def random_player():
    global stranger_invite
    if stranger_invite is None:
        this_id, other_id = create_game()
        if random.choice((True, False)):
            this_id, other_id = other_id, this_id
        stranger_invite = other_id
    else:
        this_id = stranger_invite
        stranger_invite = None
    return redirect(f'/game/{this_id}')


def main():
    app.run(host="0.0.0.0")


if __name__ == "__main__":
    main()
