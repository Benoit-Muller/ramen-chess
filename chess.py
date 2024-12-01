import warnings

White = True
Black = False

class Piece:
    def __init__(self, color):
        self.color = color
    def __str__(self):
        return self.symbol

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
    def valid_movement(self, move):
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
    def valid_movement(self, move):
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
    def valid_movement(self, move):
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
    def valid_movement(self, move):
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
    def valid_movement(self, move): 
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
    def valid_movement(self, move):
        col = move.end[0] - move.start[0]
        row = move.end[1] - move.start[1]
        return abs(col) <= 1 and abs(row) <= 1

class Move:
    def __init__(self, start, end):
        self.start = start
        self.end = end

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
