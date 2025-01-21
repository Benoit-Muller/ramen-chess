import warnings

White = True
Black = False

class Piece:
    def __init__(self, color):
        self.color = color
    def __str__(self):
        return self.symbol

class Position:
    def __init__(self, col, row):
        if not (0 <= self.col < 8 and 0 <= self.row < 8):
            raise ValueError(f"Invalid position: ({self.col}, {self.row })")
        self.col = col
        self.row = row
    def __str__(self):
        return f"{chr(97 + self.col)}{self.row + 1}"
    def __add__(self, other):
        dcol, drow = other
        return Position(self.col + dcol, self.row + drow)
    def __getitem__(self, index):
        if index == 0:
            return self.col
        elif index == 1:
            return self.row
        else:
            raise IndexError("Index out of range.")
    def __eq__(self, other):
        return self.col == other.col and self.row == other.row

class Move:
    def __init__(self, start, end, promotion=None):
        if not isinstance(start, Position):
            start = Position(*start)
        if not isinstance(end, Position):
            end = Position(*end)
        if start == end:
            raise ValueError("Start and end positions are the same.")
        self.start = start
        self.end = end
        self.promotion = promotion

class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.type = "pawn"
        if color == White:
            self.name = "P"
            self.symbol = "♙"
        else:
            self.name = "p"
            self.symbol = "♟"
    def pseudo_legal(self, move):
        col = move.end[0] - move.start[0]
        row = move.end[1] - move.start[1]
        if self.color == White:
            return abs(col) <= 1 and row == 1
        else:
            return abs(col) <= 1 and row == -1

class Rook(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.type = "rook"
        if color == White:
            self.name = "R"
            self.symbol = "♖"
        else:
            self.name = "r"
            self.symbol = "♜"
    def pseudo_legal(self, move):
        col = move.end[0] - move.start[0]
        row = move.end[1] - move.start[1]
        return col == 0 or row == 0

class Knight(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.type = "knight"
        if color == White:
            self.name = "N"
            self.symbol = "♘"
        else:
            self.name = "n"
            self.symbol = "♞"
    def pseudo_legal(self, move):
        col = move.end[0] - move.start[0]
        row = move.end[1] - move.start[1]
        return abs(col*row) == 2

class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.type = "bishop"
        if color == White:
            self.name = "B"
            self.symbol = "♗"
        else:
            self.name = "b"
            self.symbol = "♝"
    def pseudo_legal(self, move):
        col = move.end[0] - move.start[0]
        row = move.end[1] - move.start[1]
        return abs(col) == abs(row)

class Queen(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.type = "queen"
        if color == White:
            self.name = "Q"
            self.symbol = "♕"
        else:
            self.name = "q"
            self.symbol = "♛"
    def pseudo_legal(self, move): 
        col = move.end[0] - move.start[0]
        row = move.end[1] - move.start[1]
        return col == 0 or row == 0 or abs(col) == abs(row)

class King(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.type = "king"
        if color == White:
            self.name = "K"
            self.symbol = "♔"
        else:
            self.name = "k"
            self.symbol = "♚"
    def pseudo_legal(self, move):
        col = move.end[0] - move.start[0]
        row = move.end[1] - move.start[1]
        return abs(col) <= 1 and abs(row) <= 1

class Board:
    def __init__(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]

    def set_starting_position(self):
        self.clear()
        pieces= [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for col in range(8):
            self[col,0] = pieces[col](White)
            self[col,1] = Pawn(White)
            self[col,6] = Pawn(Black)
            self[col,7] = pieces[col](Black)

    def __getitem__(self, position):
        return self.grid[position[0]][position[1]]
    def __setitem__(self, position, piece):
        self.grid[position[0]][position[1]] = piece

    def move_piece(self, move, show=False):
        if self[move.start] is None:
            warnings.warn("Start square is empty.", Warning)
        else:
            capture = self[move.end]
            self[move.end] = self[move.start]
            self.clear(move.start)
            if show:
                print(self)
            return capture

    def clear(self, position=None):
        if position is not None:
            self[position] = None
        else:
            self.grid = [[None for _ in range(8)] for _ in range(8)]

    def __str__(self):
        s = ""
        for row in range(7, -1, -1):
            s += str(row + 1) + "| "
            for col in range(8):
                piece = self.grid[col][row]
                s += (str(piece) if piece else '.') + " "
            s += "\n"
        s += "   a b c d e f g h"
        return s

class Game:
    def __init__(self):
        self.board = Board()
        self.board.set_starting_position()
        self.turn = White
        self.moves = []