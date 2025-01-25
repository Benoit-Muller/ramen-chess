import warnings

WHITE = True
BLACK = False

class Piece:
    types = ["pawn", "rook", "knight", "bishop", "queen", "king"]
    type_ids = {type: i for i, type in enumerate(types)}
    names_white = ["P", "R", "N", "B", "Q", "K"]
    names_black = ["p", "r", "n", "b", "q", "k"]
    symbols_white = ["♙", "♖", "♘", "♗", "♕", "♔"]
    symbols_black = ["♟", "♜", "♞", "♝", "♛", "♚"]
    def __init__(self, color):
        self.color = color
    def __str__(self):
        return self.symbol
    def __eq__(self, value):
        return self.color == value.color and self.type == value.type
    def pseudo_legal_slide(self, board, start, dpos):
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
            #TODO: implement



            

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
        start= Position(s[0], s[1])
        end = Position(s[2], s[3])
        if len(s) == 5:
            promotion = s[4]
        else:
            promotion = None
        return Move(start, end, promotion)

class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.type = "pawn"
        if color == WHITE:
            self.name = "P"
            self.symbol = "♙"
        else:
            self.name = "p"
            self.symbol = "♟"
    def pseudo_legal_moves(self, board, start):
        moves=[]
        sign = 1 if self.color == BLACK else -1
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
                piece = board[end- (0, sign)]
                if isinstance(piece, Pawn) and piece.color != self.color:
                    moves.append(Move(start, end))
        # handle promotions of added pawn moves
        for move in moves:
            if move.end.row in [0, 7]:
                move.promotion = Queen(self.color)
                moves.append(Move(start, end, promotion="Q"))
                moves.append(Move(start, end, promotion="R"))
                moves.append(Move(start, end, promotion="B"))
                moves.append(Move(start, end, promotion="N"))

                


class Rook(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.type = "rook"
        if color == WHITE:
            self.name = "R"
            self.symbol = "♖"
        else:
            self.name = "r"
            self.symbol = "♜"
    def pseudo_legal_moves(self, board, start):
        moves = []
        for dpos in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            moves += self.pseudo_legal_slide(board, start, dpos)
        return moves

class Knight(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.type = "knight"
        if color == WHITE:
            self.name = "N"
            self.symbol = "♘"
        else:
            self.name = "n"
            self.symbol = "♞"
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
        super().__init__(color)
        self.type = "bishop"
        if color == WHITE:
            self.name = "B"
            self.symbol = "♗"
        else:
            self.name = "b"
            self.symbol = "♝"
    def pseudo_legal_moves(self, board, start):
        moves = []
        for dpos in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
            moves += self.pseudo_legal_slide(board, start, dpos)
        return moves

class Queen(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.type = "queen"
        if color == WHITE:
            self.name = "Q"
            self.symbol = "♕"
        else:
            self.name = "q"
            self.symbol = "♛"
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
        super().__init__(color)
        self.type = "king"
        if color == WHITE:
            self.name = "K"
            self.symbol = "♔"
        else:
            self.name = "k"
            self.symbol = "♚"
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
        self[move.end] = self[move.start] # TODO: fix promotion
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