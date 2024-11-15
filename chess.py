import warnings

class Piece:
    def __init__(self, name, colour):
        self.name = name
        self.colour = colour
    
    def __str__(self):
        return self.name

White = True
Black = False

class Pawn(Piece):
    def __init__(self, colour):
        Piece.__init__(self, "pawn", colour)
        if colour == White:
            self.name = "P"
        else:
            self.name = "p"

class Rook(Piece):
    def __init__(self, colour):
        Piece.__init__(self, "rook", colour)
        if colour == White:
            self.name = "R"
        else:
            self.name = "r"

class Knight(Piece):
    def __init__(self, colour):
        Piece.__init__(self, "knight", colour)
        if colour == White:
            self.name = "N"
        else:
            self.name = "n"

class Bishop(Piece):
    def __init__(self, colour):
        Piece.__init__(self, "bishop", colour)
        if colour == White:
            self.name = "B"
        else:
            self.name = "b"

class Queen(Piece):
    def __init__(self, colour):
        Piece.__init__(self, "queen", colour)
        if colour == White:
            self.name = "Q"
        else:
            self.name = "q"

class King(Piece):
    def __init__(self, colour):
        Piece.__init__(self, "king", colour)
        if colour == White:
            self.name = "K"
        else:
            self.name = "k"

class Move:
    def __init__(self, start, end):
        if isinstance(start, str) and isinstance(end, str):
            start = self.algebraic_to_coordinate(start)
            end = self.algebraic_to_coordinate(end)
        if not (0 <= start[0] < 8 and 0 <= start[1] < 8):
            raise ValueError("Start position is off the board.")
        if not (0 <= end[0] < 8 and 0 <= end[1] < 8):
            raise ValueError("End position is off the board.")
        self.start = start
        self.end = end
    
    def algebraic_to_coordinate(self, algebraic):
        file = ord(algebraic[0].lower()) - ord('a')
        rank = int(algebraic[1]) - 1
        return (file, rank)
    
    def coordinate_to_algebraic(self, coordinate):
        file = chr(coordinate[0] + ord('a'))
        rank = str(coordinate[1] + 1)
        return file + rank

class Board:
    def __init__(self, empty=False):
        self.grid = [[None for row in range(8)] for col in range(8)]
        if not empty:
            self.add_starting_pieces()
    def __str__(self):
        s = ""
        for row in range(7, -1, -1):
            s += str(row + 1) + "| "
            for col in range(8):
                if self.grid[col][row] is None:
                    s += "."
                else:
                    s += str(self.grid[col][row])
                s+= " "
            s += "\n"
        s +=  "  ––––––––––––––––\n  a b c d e f g h"
        return s
    def clear(self, place=None):
        if place == None:
            for col in range(8):
                for row in range(8):
                    self.grid[col][row] = None
        else:
            self.grid[place[0]][place[1]] = None
            
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

    def starting_position(self):
        self.clear()
        self.add_starting_pieces()

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
class Game:
    def _init_(self):
        self.board = Board()
        self.board.starting_position()
        self.turn = White
        self.moves = []
        self.result = None
        self.move_number = 1
        self.move_history = []
        self.counter_50_move_rule = 0
        
    def valid_piece_move(self,move):
        col= move.end[0] - move.start[0]
        row= move.end[1] - move.start[1]
        piece = self.board.get_piece(move.start)
        if piece is None or move.start == move.end:
            return False
        if piece.name == "rook":
            return col == 0 or row == 0
        if piece.name == "knight":
            return abs(col*row) == 2
        if piece.name == "bishop":
            return abs(col) == abs(row)
        if piece.name == "queen":
            return col == 0 or row == 0 or abs(col) == abs(row)
        if piece.name == "king":
            return abs(col) <= 1 and abs(row) <= 1
        if piece.name == "pawn":
            if piece.colour == White:
                return abs(col) <= 1 and row == 1
            else:
                return abs(col) <= 1 and row == -1
        
