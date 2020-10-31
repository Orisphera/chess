from abc import ABCMeta, abstractmethod

WHITE = 1
BLACK = 2


# Удобная функция для вычисления цвета противника
def opponent(color):
    if color == WHITE:
        return BLACK
    else:
        return WHITE


def print_board(board):  # Распечатать доску в текстовом виде (см. скриншот)
    print('     +----+----+----+----+----+----+----+----+')
    for row in range(7, -1, -1):
        print(' ', row, end='  ')
        for col in range(8):
            print('|', board.cell(row, col), end=' ')
        print('|')
        print('     +----+----+----+----+----+----+----+----+')
    print(end='        ')
    for col in range(8):
        print(col, end='    ')
    print()


def correct_coords(row, col):
    """
    Функция проверяет, что координаты (row, col) лежат
    внутри доски
    """
    return 0 <= row < 8 and 0 <= col < 8


def get_piece_picture(piece):
    return '' if piece is None else piece.picture()


def player_root(color):
    return 'бел' if color == WHITE else 'чёрн'


class Board:
    def __init__(self):
        self.rows_n = self.cols_n = 8
        self.ckr, self.okr = 0, 7
        self.ckc = self.okc = 4
        self.color = WHITE
        self.field = []
        ''' :type: list[list[Piece | None]] '''
        for row in range(8):
            self.field.append([None] * 8)
        self.field[0] = [
            Rook(WHITE), Knight(WHITE), Bishop(WHITE), Queen(WHITE),
            King(WHITE), Bishop(WHITE), Knight(WHITE), Rook(WHITE)
        ]
        self.field[1] = [
            Pawn(WHITE), Pawn(WHITE), Pawn(WHITE), Pawn(WHITE),
            Pawn(WHITE), Pawn(WHITE), Pawn(WHITE), Pawn(WHITE)
        ]
        self.field[6] = [
            Pawn(BLACK), Pawn(BLACK), Pawn(BLACK), Pawn(BLACK),
            Pawn(BLACK), Pawn(BLACK), Pawn(BLACK), Pawn(BLACK)
        ]
        self.field[7] = [
            Rook(BLACK), Knight(BLACK), Bishop(BLACK), Queen(BLACK),
            King(BLACK), Bishop(BLACK), Knight(BLACK), Rook(BLACK)
        ]
        self.last_moved = None
        ''' :type: Piece | None '''
        self.rev_moves_p1 = 1
        self.enabled = [[True] * self.cols_n for _ in range(self.rows_n)]
        self.message = ''

    def rows(self, player):
        return range(self.rows_n) if player == WHITE else range(self.rows_n - 1, -1, -1)

    def cols(self, player):
        return range(self.cols_n) if player == BLACK else range(self.cols_n - 1, -1, -1)

    def char_at(self, r, c):
        return get_piece_picture(self.field[r][c])

    def can_move(self, r, c, can_move):
        return can_move and self.enabled[r][c]

    def get_color(self, r, c, can_move):
        ans = ("white" if (r + c) % 2 else "black")
        if self.can_move(r, c, can_move):
            ans += "-red"
        return ans

    def _promote(self, row, col, piece):
        self.tk_promote_bar.pack_forget()
        for promote_btn in self.tk_promote_btns:
            promote_btn.pack_forget()
            self.tk_promote_btns.clear()
        self.field[row][col] = piece
        self.reset_gui()

    def castling(self, new_king_col, move=True):
        """
        :param new_king_col: new king column, NOT the rook column (6 = short castling, 2 = long)
        :param move: whether to move (True) or only check the conditions (False)
        """
        row = self.ckr
        row_a = self.field[row]
        if new_king_col == 6:
            new_rook_col, rook_col = 5, 7
        elif new_king_col == 2 and row_a[1] is None:
            new_rook_col, rook_col = 3, 0
        else:
            return False
        king = row_a[4]
        if self.ckc != 4 or king.moved:
            return False
        rook = row_a[rook_col]
        if rook is None or rook.moved:
            return False
        for col in 4, new_king_col, new_rook_col:
            if col != 4 and row_a[col] is not None or self.is_under_attack(row, col, opponent(
                    self.current_player_color())):
                return False
        if move:
            row_a[4] = row_a[rook_col] = None
            row_a[new_king_col] = king
            row_a[new_rook_col] = rook
            self.change_color()
            self.okc = new_king_col
        return True

    def castling0(self):  # old
        return self.castling(2)

    def castling7(self):  # old
        return self.castling(6)

    def cell(self, row, col):  # unused
        """
        Возвращает строку из двух символов. Если в клетке (row, col)
        находится фигура, символы цвета и фигуры. Если клетка пуста,
        то два пробела.
        """
        piece = self.field[row][col]
        if piece is None:
            return '  '
        return str(piece)

    def current_player_color(self):
        return self.color

    def change_color(self):
        if self.last_moved is not None:
            self.last_moved.last_move = 0, None
        self.ckc, self.ckr, self.okc, self.okr = self.okc, self.okr, self.ckc, self.ckr
        self.color = opponent(self.color)

    def get_piece(self, row, col):  # unused
        if correct_coords(row, col):
            return self.field[row][col]

    def is_under_attack(self, row, col, color=None):  # used for check check
        if color is None:
            color = opponent(self.field[row][col].get_color())
        for row2, pieces in enumerate(self.field):
            for col2, piece in enumerate(pieces):
                if (piece is not None and piece.get_color() == color and
                        piece.can_move(self, row2, col2, row, col)):
                    return True
        return False

    def move_and_promote_pawn(self, row, col, row1, col1, char):
        if not correct_coords(row, col) or not correct_coords(row1, col1):
            return False
        pawn = self.field[row][col]
        if not isinstance(pawn, Pawn) or pawn.color != self.color:
            return False
        if self.color == WHITE:
            rows = 6, 7
        else:
            rows = 1, 0
        if (row, row1) != rows:
            return False
        taken = self.field[row1][col1]
        if col != col1 if taken is None else abs(col - col1) != 1 or taken.color == self.color:
            return False
        char1 = char.lower()
        chars = 'qrb''n'
        if len(char) > 1 or char1 not in chars:
            return False
        self.field[row][col] = None
        self.field[row1][col1] = [Queen, Rook, Bishop, Knight][chars.index(char1)](self.color)
        self.change_color()
        return True

    def move_piece(self, row, col, row1, col1, only_check=False, castle=False, gui=False):
        """
        Переместить фигуру из точки (row, col) в точку (row1, col1).
        Если перемещение возможно, метод выполнит его (если не only_check) и вернёт True.
        Если нет --- вернёт False (в режиме 3 поведение не определено)
        :param row: old row
        :param col: old column
        :param row1: new row
        :param col1: new column
        :param castle: can castle
        :param only_check: whether to only check whether the move is possible
        :param gui: whether to call reset_gui after move or not; also, if False, pawn reached last
        row in this move becomes inactive forever
        """
        if not correct_coords(row, col) or not correct_coords(row1, col1):
            return False
        piece = self.field[row][col]
        if piece is None or piece.get_color() != self.current_player_color():
            return False
        if castle and isinstance(piece, King) and row == row1 and self.castling(col1,
                                                                                not only_check):
            if gui:
                self.reset_gui()
            return True
        taken_piece = self.field[row1][col1]
        if (taken_piece is not None and taken_piece.get_color() == self.current_player_color() or
                not piece.can_move(self, row, col, row1, col1)):
            return False
        self.field[row][col] = None  # Снять фигуру.
        self.field[row1][col1] = piece  # Поставить на новое место.
        if isinstance(piece, King):
            self.ckc, self.ckr = col1, row1
        incorrect = self.is_under_attack(self.ckr, self.ckc)
        if only_check or incorrect:  # FIXME: strange bug before I moved the king check
            #                          duplicating it
            if isinstance(piece, King):
                self.ckc, self.ckr = col, row
            self.field[row][col] = piece
            self.field[row1][col1] = taken_piece
            piece.undo(self, row, col, row1, col1)
            return not incorrect
        piece.moved = True
        self.change_color()
        self.last_moved = piece
        if gui:
            if isinstance(piece, Pawn) and row1 in (0, 7):
                self.tk_message.configure(text='Выберите фигуру, в которую Вы хотите\n'
                                               'превратить пешку:')
                for row in range(8):
                    for col in range(8):
                        self.disable_btn(row, col)
                medium = Font(size=15)
                for piece_type in Rook, Knight, Queen, Bishop:
                    new_piece = piece_type(piece.get_color())
                    promote_btn = tk.Button(self.tk_promote_bar, command=lambda np=new_piece:
                                            self._promote(col1, row1, np), font=medium)
                    draw_piece(promote_btn, new_piece)
                    promote_btn.pack(side=tk.LEFT)
                    self.tk_promote_btns.append(promote_btn)
            else:
                self.reset_gui()
        return True

    def prepare_move(self, row, col):
        for row1 in range(8):
            for col1 in range(8):
                if self.move_piece(row, col, row1, col1, True, True):
                    self.enable_btn(row1, col1, lambda r=row, c=col, r1=row1, c1=col1:
                                    self.move_piece(r, c, r1, c1, False, True, True))
                else:
                    self.disable_btn(row1, col1)

    def reset_gui(self):
        """
        Настраивает кнопки для выбора фигуры для хода и обрабатывает конец игры
        """
        not_ended = False
        for row in range(8):
            for col in range(8):
                btn = self.tk_field[row][col]
                piece = self.field[row][col]
                if piece is None:
                    btn.configure(text='  ')
                else:
                    draw_piece(btn, piece)
                if piece is None or piece.color != self.color or not piece.is_active(self, row, col):
                    self.disable_btn(row, col)
                else:
                    self.enable_btn(row, col, lambda row1=row, col1=col: self.prepare_move(row1,
                                                                                           col1))
                    not_ended = True
        check = self.is_under_attack(self.ckr, self.ckc)
        if not_ended:
            text = f"Ход {player_root(self.current_player_color())}ых"
            if check:
                text = 'Шах! ' + text
        elif check:
            winner_root = player_root(opponent(self.current_player_color())).title()
            text = f"{winner_root}ые победили!"
        else:
            text = 'Пат'
        self.tk_message.configure(text=text)


class Piece(metaclass=ABCMeta):
    def __init__(self, color):
        self.color = color
        self.last_move = self.last_move_bk = 0, None  # Pawn only
        self.moved = False  # For castling

    def __str__(self):
        color = self.get_color()
        c = 'w' if color == WHITE else 'b'
        return c + self.char()

    @abstractmethod
    def can_move(self, board, row, col, row1, col1):
        """
        :type board: Board
        :type row: int
        :type col: int
        :type row1: int
        :type col1: int
        """
        return True

    @abstractmethod
    def char(self):
        return 'F'

    def get_color(self):
        return self.color

    def is_active(self, board, row, col):
        for row1 in range(8):
            for col1 in range(8):
                if (row, col) != (row1, col1) and board.move_piece(row, col, row1, col1, 2, True):
                    return True
        return False

    @abstractmethod
    def _picture(self):
        return "?"

    def picture(self):
        ans = self._picture()
        if self.color == BLACK:
            return chr(ord(ans) + 6)
        return ans

    def undo(self, board, row, col, row1, col1):
        """
        Отменяет "взятие на проходе" и изменение last_move для пешки
        """
        pass


class Rook(Piece):
    def char(self):
        return 'R'

    def _picture(self):
        return '♖'

    def can_move(self, board, row, col, row1, col1):
        # Невозможно сделать ход в клетку, которая не лежит в том же ряду
        # или столбце клеток.
        if row != row1 and col != col1:
            return False

        step = 1 if (row1 >= row) else -1
        for r in range(row + step, row1, step):
            # Если на пути по горизонтали есть фигура
            if board.field[r][col] is not None:
                return False

        step = 1 if (col1 >= col) else -1
        for c in range(col + step, col1, step):
            # Если на пути по вертикали есть фигура
            if board.field[row][c] is not None:
                return False

        return True


class Pawn(Piece):
    def char(self):
        return 'P'

    def _picture(self):
        return '♙'

    def bk1m(self, new1m=(0, None)):
        self.last_move_bk = self.last_move
        self.last_move = new1m
        return True

    def can_move(self, board, row, col, row1, col1):
        if self.color == WHITE:
            direction = 1
            start_row = 1
        else:
            direction = -1
            start_row = 6

        # moves one cell
        moc = row + direction == row1
        takes = board.field[row1][col1] is not None  # взятие не на проходе
        if col != col1:  # взятие (в т. ч. на проходе)
            if not moc or abs(col - col1) != 1:
                return False
            if takes:
                return self.bk1m()
            taken_piece = board.field[row][col1]
            if taken_piece is not None and taken_piece.get_color() != self.color and \
                    taken_piece.last_move[0] == 1:
                board.field[row][col1] = None
                return self.bk1m((2, taken_piece))
            return False

        if takes:  # нельзя брать обычным ходом
            return False

        # ход на 1 клетку
        if moc:
            return self.bk1m()

        # ход на 2 клетки из начального положения
        if (row == start_row
                and row + 2 * direction == row1
                and board.field[row + direction][col] is None):
            return self.bk1m((1, None))

        return False

    def undo(self, board, row, col, row1, col1):
        if self.last_move[0] == 2:
            board.field[row][col1] = self.last_move[1]
        self.last_move = self.last_move_bk


class Knight(Piece):
    def char(self):
        return 'N'  # kNight, буква 'K' уже занята королём

    def _picture(self):
        return '♘'

    def can_move(self, board, row, col, row1, col1):
        return {abs(col - col1), abs(row - row1)} == {1, 2}


class King(Piece):
    def char(self):
        return 'K'

    def _picture(self):
        return '♔'

    def can_move(self, board, row, col, row1, col1):
        return {row - row1, col - col1, 1, -1, 0} == {1, -1, 0}


class Queen(Piece):
    def char(self):
        return 'Q'

    def _picture(self):
        return '♕'

    def can_move(self, board, row, col, row1, col1):
        return Bishop.can_move(self, board, row, col, row1, col1) or \
               Rook.can_move(self, board, row, col, row1, col1)


class Bishop(Piece):
    def char(self):
        return 'B'

    def _picture(self):
        return '♗'

    def can_move(self, board, row, col, row1, col1):
        # Невозможно сделать ход в клетку, которая не лежит на той же диагонали.
        if abs(row - row1) != abs(col - col1):
            return False

        step1 = 1 if (row1 >= row) else -1
        step2 = 1 if (col1 >= col) else -1
        c = col
        for r in range(row + step1, row1, step1):
            c += step2
            # Если на пути по диагонали есть фигура
            if board.field[r][c] is not None:
                return False

        return True