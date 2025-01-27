import warnings

WHITE = True
BLACK = False

class Piece:
    types = ["pawn", "rook", "knight", "bishop", "queen", "king"]
    names_white = ["P", "R", "N", "B", "Q", "K"]
    names_black = ["p", "r", "n", "b", "q", "k"]
    symbols_white = ["♙", "♖", "♘", "♗", "♕", "♔"]
    symbols_black = ["♟", "♜", "♞", "♝", "♛", "♚"]
    def __init__(self, color, type):
        if self.__class__ == Piece:
            raise TypeError("Piece is an abstract class and cannot be instantiated directly.")
        self.color = color
        self.type = type
        if color == WHITE:
            self.name = self.names_white[self.types.index(type)]
            self.symbol = self.symbols_white[self.types.index(type)]
        else:
            self.name = self.names_black[self.types.index(type)]
            self.symbol = self.symbols_black[self.types.index(type)]
    def __str__(self):
        return self.symbol
    def __eq__(self, value):
        return isinstance(value, Piece) and value.name == self.name
    def pseudo_legal_slide(self, board, start, dpos):
        """ Return a list of pseudo-legal sliding moves in the direction dpos. """
        moves = []
        end=start
        while True:
            try:
                end = end + dpos
            except:
                break
            else:
                piece = board[end]
                if piece is None:
                    moves.append(Move(start, end))
                else:
                    if piece.color != self.color:
                        moves.append(Move(start, end))
                    break
        return moves
    @staticmethod
    def from_string(name):
        color = name.isupper()
        if name.lower() == "p":
            return Pawn(color)
        elif name.lower() == "r":
            return Rook(color)
        elif name.lower() == "n":
            return Knight(color)
        elif name.lower() == "b":
            return Bishop(color)
        elif name.lower() == "q":
            return Queen(color)
        elif name.lower() == "k":
            return King(color)
        else:
            raise ValueError(f"Invalid piece name: {name}")

class Position:
    def __init__(self, col, row):
        if isinstance(col, str):
            col = ord(col) - ord('a')
        if isinstance(row, str):
            row = int(row) - 1
        if not (0 <= col < 8 and 0 <= row < 8):
            raise ValueError(f"Invalid position: ({col}, {row})")
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
    @staticmethod
    def from_string(s):
        return Position(s[0], s[1])

class Move:
    def __init__(self, start, end, promotion=None):
        if not isinstance(start, Position):
            start = Position(*start)
        if not isinstance(end, Position):
            end = Position(*end)
        if start == end:
            raise ValueError("Start and end positions are the same.")
        if isinstance(promotion, str):
            promotion = Piece.from_type(promotion, start.color)
        self.start = start
        self.end = end
        self.promotion = promotion
    def __str__(self):
        return str(self.start) + str(self.end) + (self.promotion or "")
    def __eq__(self, other):
        return self.start == other.start and self.end == other.end and self.promotion == other.promotion
    @staticmethod
    def from_string(s):
        start= Position.from_string(s[:2])
        end = Position.from_string(s[2:4])
        if len(s) == 5:
            promotion = Piece.from_string(s[4])
        else:
            promotion = None
        return Move(start, end, promotion)

class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color, "pawn")
    def pseudo_legal_moves(self, board, start):
        moves=[]
        sign = 1 if self.color == WHITE else -1
        # one forward
        end = start + (0, 1)  # should always work
        if board[end] is None:
            moves.append(Move(start, end))
        # two forward
        if (start.row == 1 and self.color == WHITE) or (start.row == 6 and self.color == BLACK):
            end = start + (0, sign*2)
            if board[end] is None and board[start + (0, sign)] is None:
                moves.append(Move(start, end))
        # take
        for dcol in [-1, 1]:
            try:
                end = start + (dcol, sign)
            except:
                continue
            else:
                piece = board[end]
                if piece is not None and piece.color != self.color:
                    moves.append(Move(start, end))
        # en-passant
        if self.color == WHITE:
            row = 4
        else:
            row = 3 
        for dcol in [-1, 1]:
            try:
                end = start + (dcol, sign)
            except:
                continue
            else:
                piece = board[end + (0, -sign)]
                if isinstance(piece, Pawn) and piece.color != self.color:
                    moves.append(Move(start, end))
        # handle promotions of added pawn moves
        for move in moves:
            if move.end.row in [0, 7]:
                move.promotion = Queen(self.color)
                for promotion in [Rook, Bishop, Knight]:
                    moves.append(Move(move.start, move.end, promotion(self.color)))
        return moves

class Rook(Piece):
    def __init__(self, color):
        super().__init__(color, "rook")
    def pseudo_legal_moves(self, board, start):
        moves = []
        for dpos in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            moves += self.pseudo_legal_slide(board, start, dpos)
        return moves

class Knight(Piece):
    def __init__(self, color):
        super().__init__(color, "knight")
    def pseudo_legal_moves(self, board, start):
        moves = []
        for dpos in [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)]:
            try:
                end = start + dpos
            except:
                continue
            else:
                piece = board[end]
                if piece is None or piece.color != self.color:
                    moves.append(Move(start, end))
        return moves


class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color, "bishop")
    def pseudo_legal_moves(self, board, start):
        moves = []
        for dpos in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
            moves += self.pseudo_legal_slide(board, start, dpos)
        return moves

class Queen(Piece):
    def __init__(self, color):
        super().__init__(color, "queen")
    def pseudo_legal_moves(self, board, start):
        moves = []
        for dcol in [-1, 0, 1]:
            for drow in [-1, 0, 1]:
                if dcol == 0 and drow == 0:
                    continue
                dpos = (dcol, drow)
                moves += self.pseudo_legal_slide(board, start, dpos)
        return moves

class King(Piece):
    def __init__(self, color):
        super().__init__(color, "king")
    def pseudo_legal_moves(self, board, start):
        moves = []
        for dcol in [-1, 0, 1]:
            for drow in [-1, 0, 1]:
                if dcol == 0 and drow == 0:
                    continue
                dpos = (dcol, drow)
                try:
                    end = start + dpos
                except:
                    continue
                else:
                    piece = board[end]
                    if piece is None or piece.color != self.color:
                        moves.append(Move(start, end))
        #castling moves
        if self.color == WHITE:
            row = 0
        else:
            row = 7
        if start == Position(4, row):
            if board[5, row] is None and board[6, row] is None and board[7, row] == Rook(self.color):
                moves.append(Move(start, Position(6, row)))
            if board[3, row] is None and board[2, row] is None and board[1, row] is None and board[0, row] == Rook(self.color):
                moves.append(Move(start, Position(2, row)))
        return moves

class Board:
    def __init__(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]

    def set_starting_position(self):
        self.clear()
        pieces= [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for col in range(8):
            self[col,0] = pieces[col](WHITE)
            self[col,1] = Pawn(WHITE)
            self[col,6] = Pawn(BLACK)
            self[col,7] = pieces[col](BLACK)

    def __getitem__(self, position):
        return self.grid[position[0]][position[1]]
    
    def __setitem__(self, position, piece):
        self.grid[position[0]][position[1]] = piece

    def move(self, move, show=False):
        if isinstance(move, str):
            move = Move.from_string(move)
        if self[move.start] is None:
            warnings.warn("Start square is empty.", Warning)
        capture = self[move.end]
        if move.promotion is None:
            self[move.end] = self[move.start]
        else:
            self[move.end] = move.promotion
        self.clear(move.start)
        # Handle castling
        if isinstance(self[move.end], King) and abs(move.start.col - move.end.col) == 2:
            if move.end.col == 6:  # Kingside castling
                self[Position(5, move.start.row)] = self[Position(7, move.start.row)]
                self.clear(Position(7, move.start.row))
            elif move.end.col == 2:  # Queenside castling
                self[Position(3, move.start.row)] = self[Position(0, move.start.row)]
                self.clear(Position(0, move.start.row))
        # Handle en-passant
        if isinstance(self[move.end], Pawn) and move.start.col != move.end.col and self[move.end] is None:
            capture = self.clear(move.start + (move.end.col - move.start.col, 0))
        if show: 
            print(self)
        return capture

    def clear(self, position=None):
        if position is not None:
            piece = self[position]
            self[position] = None
            return piece
        else:
            self.grid = [[None for _ in range(8)] for _ in range(8)]

    def __str__(self):
        s = ""
        for row in range(7, -1, -1):
            s += str(row + 1) + " | "
            for col in range(8):
                piece = self.grid[col][row]
                s += (str(piece) if piece else '.') + " "
            s += "\n"
        s += "   ––––––––––––––––\n"
        s += "    a b c d e f g h"
        return s
    
    def pseudo_legal_moves(self, color):
        moves = []
        for col in range(8):
            for row in range(8):
                piece = self[col, row]
                if piece is not None and piece.color == color:
                    moves += piece.pseudo_legal_moves(self, Position(col, row))
        return moves

class Game:
    def __init__(self):
        self.board = Board()
        self.board.set_starting_position()
        self.moves = []
    def move(self, move):
        self.moves.append(move)
        return self.board.move(move)
    def turn(self):
        return len(self.moves) % 2 == 0
    def __str__(self):
        return str(self.board)
    def pseudo_legal_moves(self):
        return self.board.pseudo_legal_moves(self.turn())