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
        self.col = col
        self.row = row
        if not (0 <= self.col < 8 and 0 <= self.row < 8):
            raise ValueError(f"Invalid position: ({self.col}, {self.row })")
    def __str__(self):
        return f"{chr(97 + self.col)}{self.row + 1}"
    def __sub__ (self, other):
        return Move((self.col, self.row), (other.col, other.row))
    def __add__(self, dcol, drow):
        return Position(self.col + dcol, self.row + drow)
    def __getitem__(self, index):
        if index == 0:
            return self.col
        elif index == 1:
            return self.row
        else:
            raise IndexError("Index out of range.")

class Move:
    def __init__(self, start, end, promotion=None):
        self.start = start
        self.end = end
        self.promotion = promotion

        if not (0 <= self.start[0] < 8 and 0 <= self.start[1] < 8):
            raise ValueError(f"Invalid start position: {self.start}")
        if not (0 <= self.end[0] < 8 and 0 <= self.end[1] < 8):
            raise ValueError(f"Invalid end position: {self.end}")
        if self.start == self.end:
            raise ValueError("Start and end positions are the same.")

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
        self.starting_position()

    def starting_position(self):
        self.clear()
        self.add_starting_pieces()

    def add_starting_pieces(self):
        for col in range(8):
            self.set_piece((col, 1), Pawn(White))
            self.set_piece((col, 6), Pawn(Black))
        self.set_piece((0, 0), Rook(White))
        self.set_piece((1, 0), Knight(White))
        self.set_piece((2, 0), Bishop(White))
        self.set_piece((3, 0), Queen(White))
        self.set_piece((4, 0), King(White))
        self.set_piece((5, 0), Bishop(White))
        self.set_piece((6, 0), Knight(White))
        self.set_piece((7, 0), Rook(White))

        self.set_piece((0, 7), Rook(Black))
        self.set_piece((1, 7), Knight(Black))
        self.set_piece((2, 7), Bishop(Black))
        self.set_piece((3, 7), Queen(Black))
        self.set_piece((4, 7), King(Black))
        self.set_piece((5, 7), Bishop(Black))
        self.set_piece((6, 7), Knight(Black))
        self.set_piece((7, 7), Rook(Black))

    def get_piece(self, place):
        return self.grid[place[0]][place[1]]

    def set_piece(self, place, piece):
        self.grid[place[0]][place[1]] = piece

    def move_piece(self, move, show=False):
        if self.get_piece(move.start) is None:
            warnings.warn("Start square is empty.", Warning)
        else:
            capture = self.get_piece(move.end)
            self.set_piece(move.end, self.get_piece(move.start))
            self.clear(move.start)
            if show:
                print(self)
            return capture

    def clear(self, place=None):
        if place:
            self.grid[place[0]][place[1]] = None
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
        self.turn = White
        self.moves = []
        self.result = None
