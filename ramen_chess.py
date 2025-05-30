import warnings
import copy
import chess

class KingCaptureError(ValueError):
    pass

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
    def __repr__(self):
        return self.type.capitalize() + "(" + ("WHITE" if self.color == WHITE else "BLACK") + ")"
    def __eq__(self, value):
        return isinstance(value, Piece) and value.name == self.name
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

class Square:
    def __init__(self, col, row):
        if isinstance(col, str):
            col = ord(col) - ord('a')
        if isinstance(row, str):
            row = int(row) - 1
        if not (0 <= col < 8 and 0 <= row < 8):
            raise ValueError(f"Invalid square: ({col}, {row})")
        self.col = col
        self.row = row
    def __str__(self):
        return f"{chr(97 + self.col)}{self.row + 1}"
    def __repr__(self):
        return f"Square.from_string('{str(self)}')"
    def __add__(self, other):
        dcol, drow = other
        return Square(self.col + dcol, self.row + drow)
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
        return Square(s[0], s[1])

class Move:
    def __init__(self, start, end, promotion=None): # TODO: add draw/resign
        if not isinstance(start, Square):
            start = Square(*start)
        if not isinstance(end, Square):
            end = Square(*end)
        if start == end:
            raise ValueError("Start and end squares are the same.")
        if isinstance(promotion, str):
            promotion = Piece.from_type(promotion, start.color)
        self.start = start
        self.end = end
        self.promotion = promotion
    def __str__(self):
        try:
            return self.pseudo_algebraic()
        except:
            return self.uci()
    def __repr__(self):
        s= f"Move('{self.start}','{self.end}'"
        if self.promotion is not None:
            s += f",'{self.promotion.name}'"
        return s + ")" 
    def __eq__(self, other):
        return (self.start, self.end, self.promotion) == (other.start, other.end, other.promotion)
    @staticmethod
    def from_string(s):
        start= Square.from_string(s[:2])
        end = Square.from_string(s[2:4])
        if len(s) == 5:
            promotion = Piece.from_string(s[4])
        else:
            promotion = None
        return Move(start, end, promotion)
    def is_short_castling(self):
        # suppose a legal move
        return self.uci() in ["e1g1", "e8g8"] and isinstance(self.piece, King)
    def is_long_castling(self):
        # suppose a legal move
        return self.uci() in ["e1c1", "e8c8"] and isinstance(self.piece, King)
    def is_castling(self):
        # suppose a legal move
        return self.is_short_castling() or self.is_long_castling()
    def uci(self):
        return str(self.start) + str(self.end) + (self.promotion.name.lower() if self.promotion is not None else "")
    def interpret(self, board):
        self.piece = board[self.start]
        if self.piece is None:
            raise ValueError("No piece on start square.")
        self.capture = board[self.end]
        if self.capture is not None and self.capture.color == self.piece.color:
            raise ValueError("Cannot capture own piece.")
        if isinstance(self.capture, King):
            raise KingCaptureError("Last move was illegal.")
        self.is_en_passant = (
            isinstance(self.piece, Pawn) and 
            self.start.col != self.end.col and 
            board[self.end] is None
        )
        if self.is_en_passant:
            self.capture = board[self.end + (0, -1 if self.piece.color == WHITE else 1)]
        return self
    def pseudo_algebraic(self):
        # need to be interpreted first
        if self.is_short_castling():
            return "O-O"
        if self.is_long_castling():
            return "O-O-O"
        san = self.piece.name.upper()
        san += str(self.start)
        if self.capture is not None:
            san += "x"
        san += str(self.end)
        if self.promotion is not None:
            san += "=" + self.promotion.name.upper()
        return san

class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color, "pawn")
    def pseudo_legal_moves(self, game, start):
        moves=[]
        sign = 1 if self.color == WHITE else -1
        # one forward
        end = start + (0, sign)  # should always work
        if game.board[end] is None:
            moves.append(Move(start, end))
        # two forward
        if (start.row == 1 and self.color == WHITE) or (start.row == 6 and self.color == BLACK):
            end = start + (0, sign*2)
            if game.board[end] is None and game.board[start + (0, sign)] is None:
                moves.append(Move(start, end))
        # take (and en-passant)
        for dcol in [-1, 1]:
            try:
                end = start + (dcol, sign)
            except:
                continue
            else:
                piece = game.board[end]
                if piece is not None and piece.color != self.color:
                    moves.append(Move(start, end))
                if game.en_passant_target is not None:
                    if end == game.en_passant_target:
                        moves.append(Move(start, end))
        # handle promotions of added pawn moves
        for i in range(len(moves)):
            move=moves[i]
            if move.end.row in [0, 7]:
                move.promotion = Queen(self.color) # inplace modification, but should be ok
                for promotion in [Rook, Bishop, Knight]:
                    moves.append(Move(move.start, move.end, promotion(self.color)))
        return moves

class Rook(Piece):
    def __init__(self, color):
        super().__init__(color, "rook")
    def pseudo_legal_moves(self, game, start):
        moves = []
        for dpos in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            moves += self.pseudo_legal_slide(game.board, start, dpos)
        return moves
        

class Knight(Piece):
    def __init__(self, color):
        super().__init__(color, "knight")
    def pseudo_legal_moves(self, game, start):
        moves = []
        for dpos in [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)]:
            try:
                end = start + dpos
            except:
                continue
            else:
                piece = game.board[end]
                if piece is None or piece.color != self.color:
                    moves.append(Move(start, end))
        return moves


class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color, "bishop")
    def pseudo_legal_moves(self, game, start):
        moves = []
        for dpos in [(1, 1), (-1, 1), (1, -1), (-1, -1)]:
            moves += self.pseudo_legal_slide(game.board, start, dpos)
        return moves

class Queen(Piece):
    def __init__(self, color):
        super().__init__(color, "queen")
    def pseudo_legal_moves(self, game, start):
        moves = []
        for dcol in [-1, 0, 1]:
            for drow in [-1, 0, 1]:
                if dcol == 0 and drow == 0:
                    continue
                dpos = (dcol, drow)
                moves += self.pseudo_legal_slide(game.board, start, dpos)
        return moves

class King(Piece):
    def __init__(self, color):
        super().__init__(color, "king")
    def pseudo_legal_moves(self, game, start):
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
                    piece = game.board[end]
                    if piece is None or piece.color != self.color:
                        moves.append(Move(start, end))
        #castling moves
        if self.color == WHITE:
            row = 0
        else:
            row = 7
        short_path_is_clear = (game.get_castling_rights(self.color)["short"]
            and game.board[5, row] is None
            and game.board[6, row] is None )
        long_path_is_clear = (game.get_castling_rights(self.color)["long"]
            and game.board[3, row] is None
            and game.board[2, row] is None
            and game.board[1, row] is None)
        if short_path_is_clear:
            move=Move(start, start + (2, 0))
            game.move(move)
            next_moves = game.pseudo_legal_moves()
            game.undo_move()
            short_path_is_safe = True
            for next_move in next_moves:
                if next_move.end in [Square(4, row), Square(5, row), Square(6, row)]:
                    short_path_is_safe=False
                    break
            if short_path_is_safe:
                moves.append(move)
        if long_path_is_clear:
            move=Move(start, start + (-2, 0))
            game.move(move)
            next_moves = game.pseudo_legal_moves()
            game.undo_move()
            long_path_is_safe = True
            for next_move in next_moves:
                if next_move.end in [Square(4, row), Square(3, row), Square(2, row)]:
                    long_path_is_safe=False
                    break
            if long_path_is_safe:
                moves.append(move)
        return moves

class Board:
    def __init__(self,fen=None):
        if fen is not None:
            self.grid = Board.from_fen(fen).grid
        else:
            self.grid = [[None for _ in range(8)] for _ in range(8)]
    def __eq__(self, value):
        return isinstance(value, Board) and self.grid == value.grid
    def __getitem__(self, square):
        return self.grid[square[0]][square[1]]
    def __setitem__(self, square, piece):
        self.grid[square[0]][square[1]] = piece
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
    def __repr__(self):
        return "Board('" + self.fen() + "')"
    def __copy__(self):
        board= Board()
        board.grid = [row.copy() for row in self.grid]
        return board
    def __deepcopy__(self):
        return Board(self.fen())
    def copy(self):
        return self.__copy__()
    @staticmethod
    def from_fen(fen):
        board = Board()
        row = 7
        col = 0
        for c in fen:
            if c == "/":
                row -= 1
                col = 0
            elif c.isdigit():
                col += int(c)
            else:
                board[col, row] = Piece.from_string(c)
                col += 1
        return board
    def set_starting_position(self): # could be made with fen
        self.clear()
        pieces= [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for col in range(8):
            self[col,0] = pieces[col](WHITE)
            self[col,1] = Pawn(WHITE)
            self[col,6] = Pawn(BLACK)
            self[col,7] = pieces[col](BLACK)
    def move(self, move, show=False):
        if isinstance(move, str):
            move = Move.from_string(move)
        move.interpret(self)
        capture = self[move.end]
        if move.promotion is None:
            self[move.end] = self[move.start]
        else:
            self[move.end] = move.promotion
        self.clear(move.start)
        # Handle castling
        if isinstance(self[move.end], King) and abs(move.start.col - move.end.col) == 2:
            if move.end.col == 6:  # Kingside castling
                self[Square(5, move.start.row)] = self[Square(7, move.start.row)]
                self.clear(Square(7, move.start.row))
            elif move.end.col == 2:  # Queenside castling
                self[Square(3, move.start.row)] = self[Square(0, move.start.row)]
                self.clear(Square(0, move.start.row))
        # Handle en-passant
        if isinstance(self[move.end], Pawn) and move.start.col != move.end.col and self[move.end] is None:
            capture = self.clear(move.start + (move.end.col - move.start.col, 0))
            move.en_passant = True
        else:
            move.en_passant = False
        if show: 
            print(self)
        move.capture = capture
        return move
    def undo_move(self, move):
        self[move.start] = self[move.end]
        self[move.end] = move.capture
        # Handle castling
        if isinstance(self[move.start], King) and abs(move.start.col - move.end.col) == 2:
            if move.end.col == 6:
                self[Square(7, move.start.row)] = self[Square(5, move.start.row)]
                self.clear(Square(5, move.start.row))
            elif move.end.col == 2:
                self[Square(0, move.start.row)] = self[Square(3, move.start.row)]
                self.clear(Square(3, move.start.row))
        # Handle en-passant
        if isinstance(self[move.end], Pawn): 
            try:
                if move.en_passant:
                    self[move.end] = None
                    self[move.start + (move.end.col - move.start.col, 0)] = move.capture
            except:
                raise ValueError("Missing en-passant information to undo move.")
        return move
    def show_move(self, move):
        board_copy = self.copy()
        board_copy.move(move, show=True)
    def clear(self, square=None):
        if square is not None:
            piece = self[square]
            self[square] = None
            return piece
        else:
            self.grid = [[None for _ in range(8)] for _ in range(8)]
    def fen(self):
        s = ""
        for row in range(7, -1, -1):
            for col in range(8):
                piece = self.grid[col][row]
                if piece is None:
                    if len(s) > 0 and s[-1].isdigit():
                        s = s[:-1] + str(int(s[-1]) + 1)
                    else:
                        s += "1"
                else:
                    s += piece.name
            s += "/"
        s = s[:-1]
        return s

class Position:
    def __init__(self,board,turn,castling_rights,en_passant_target,halfmove_clock,fullmove_number):
        self.board=board
        self.turn=turn
        self.castling_rights=castling_rights
        self.en_passant_target=en_passant_target
        self.halfmove_clock=halfmove_clock
        self.fullmove_number=fullmove_number
    def __str__(self):
        return str(self.fen())
    def __repr__(self):
        return "Position.from_fen('" + self.fen() + "')"
    def __eq__(self, value):
        return (
            isinstance(value, Position) and 
            self.board == value.board and 
            self.turn == value.turn and 
            self.castling_rights == value.castling_rights and 
            self.en_passant_target == value.en_passant_target and 
            self.halfmove_clock == value.halfmove_clock and 
            self.fullmove_number == value.fullmove_number
        )
    def __copy__(self):
        return Position(
            self.board.copy(),
            self.turn,
            self.castling_rights.copy(),
            self.en_passant_target,
            self.halfmove_clock,
            self.fullmove_number
        )
    def __deepcopy__(self):
        return Position(
            self.board.deepcopy(),
            self.turn,
            copy.deepcopy(self.castling_rights),
            self.en_passant_target,
            self.halfmove_clock,
            self.fullmove_number
        )
    def copy(self):
        return self.__copy__()
    @staticmethod
    def starting():
        board = Board()
        board.set_starting_position()
        return Position(
            board=board,
            turn=WHITE,
            castling_rights={"white_short": True, "white_long": True, "black_short": True, "black_long": True},
            en_passant_target=None,
            halfmove_clock=0,
            fullmove_number=1
        )
    @staticmethod
    def from_fen(fen):
        parts = fen.split(" ")
        board = Board.from_fen(parts[0])
        turn = parts[1] == "w"
        castling_rights = {
            "white_short": "K" in parts[2],
            "white_long": "Q" in parts[2],
            "black_short": "k" in parts[2],
            "black_long": "q" in parts[2]
        }
        en_passant_target = None if parts[3] == "-" else Square.from_string(parts[3])
        halfmove_clock = int(parts[4])
        fullmove_number = int(parts[5])
        return Position(board, turn, castling_rights, en_passant_target, halfmove_clock, fullmove_number)
    def fen(self):
        s = self.board.fen()
        s += " "
        s += "w" if self.turn == WHITE else "b"
        s += " "
        s += "K" if self.castling_rights["white_short"] else ""
        s += "Q" if self.castling_rights["white_long"] else ""
        s += "k" if self.castling_rights["black_short"] else ""
        s += "q" if self.castling_rights["black_long"] else ""
        if s[-1] == " ":
            s += "-"
        s += " "
        if self.en_passant_target is None:
            s += "-"
        else:
            s += str(self.en_passant_target)
        s += " "
        s += str(self.halfmove_clock)
        s += " "
        s += str(self.fullmove_number)
        return s
        
class Game:
    def __init__(self,position=None):
        if position is None:
            position=Position.starting()
            self.variant="standard"
        else:
            if isinstance(position,str):
                position=Position.from_fen(position)
            self.variant="from_position"
        self.board = position.board
        self.turn = position.turn
        self.castling_rights = position.castling_rights
        self.en_passant_target = position.en_passant_target
        self.halfmove_clock = position.halfmove_clock
        self.fullmove_number = position.fullmove_number
        self.moves = []
        self.positions=[]
    def __str__(self):
        s_board = str(self.board)
        s_moves = self.pgn()
        if self.is_checkmate():
            s_state = "Checkmate."
        elif self.is_stalemate():
            s_state = "Stalemate."
        else:
            s_state = "White to move." if self.turn == WHITE else "Black to move."
        return s_moves + "\n" + s_board + "\n" + s_state
    def get_castling_rights(self,color=None):
        if color is None:
            return self.castling_rights
        else:
            if color == WHITE:
                return {"short": self.castling_rights["white_short"], "long": self.castling_rights["white_long"]}
            else:
                return {"short": self.castling_rights["black_short"], "long": self.castling_rights["black_long"]}
    def position(self):
        return Position(
            board=self.board.copy(),
            turn=self.turn,
            castling_rights=copy.deepcopy(self.castling_rights),
            en_passant_target=self.en_passant_target,
            halfmove_clock=self.halfmove_clock,
            fullmove_number=self.fullmove_number
        )
    def move(self, move):
        # TODO: check if move is legal, right turn, etc.
        self.positions.append(self.position())
        move = self.board.move(move)
        self.moves.append(move)
        self.turn = not self.turn
        self.castling_rights = self.update_castling_rights(move)
        if isinstance(move.piece, Pawn) and abs(move.start.row - move.end.row) == 2:
            self.en_passant_target = move.end + (0, -1 if move.piece.color == WHITE else 1)
        else:
            self.en_passant_target = None
        self.halfmove_clock = self.halfmove_clock + 1
        if self.turn == WHITE:
            self.fullmove_number += 1
        return move
    def undo_move(self):
        if len(self.moves) == 0:
            warnings.warn("No moves to undo.")
            return
        move = self.moves.pop()
        position = self.positions.pop()
        self.board = position.board
        self.turn = position.turn
        self.castling_rights = position.castling_rights
        self.en_passant_target = position.en_passant_target
        self.halfmove_clock = position.halfmove_clock
        self.fullmove_number = position.fullmove_number
        return move
    def update_castling_rights(self,move):
        rights = self.castling_rights
        # using square but could use piece type, optimize also later
        # white
        if Square(4, 0) in [move.start, move.end]:
            rights["white_short"] = False
            rights["white_long"] = False
        elif Square(0, 0) in [move.start, move.end]:
            rights["white_long"] = False
        elif Square(7, 0) in [move.start, move.end]:
            rights["white_short"] = False
        # black
        elif Square(4, 7) in [move.start, move.end]:
            rights["black_short"] = False
            rights["black_long"] = False
        elif Square(0, 7) in [move.start, move.end]:
            rights["black_long"] = False
        elif Square(7, 7) in [move.start, move.end]:
            rights["black_short"] = False
        return rights
    def pseudo_legal_moves(self,color=None):
        if color is None:
            color = self.turn
        moves = []
        for col in range(8):
            for row in range(8):
                piece = self.board[col, row]
                if piece is not None and piece.color == color:
                    moves += piece.pseudo_legal_moves(self, Square(col, row))
        for i in range(len(moves)):
            moves[i].interpret(self.board)
        return moves
    def is_check(self,color=None):
        if color is None:
            color = self.turn
        for move in self.pseudo_legal_moves(not color):
            if isinstance(self.board[move.end], King):
                return True
        return False
    def pseudo_is_legal(self, move):
        move.interpret(self.board)
        assert move.piece.color == self.turn
        self.move(move)
        next_moves = self.pseudo_legal_moves()
        self.undo_move()
        for next_move in next_moves:
            if isinstance(next_move.capture, King):
                return False
        if move.is_castling() and False: # implemented in King.pseudo_legal_moves
            row=0 if move.piece.color==WHITE else 7
            if move.is_short_castling():
                for next_move in next_moves:
                    if next_move.end.row==row and next_move.end.col in [4,5,6]:
                        return False
            if move.is_long_castling():
                for next_move in next_moves:
                    if next_move.end.row==row and next_move.end.col in [4,3,2]:
                        return False
        return True
    def legal_moves(self):
        moves = self.pseudo_legal_moves()
        return [move for move in moves if self.pseudo_is_legal(move)]
    def is_checkmate(self):
        return self.is_check() and len(self.legal_moves()) == 0
    def is_stalemate(self):
        return not self.is_check() and len(self.legal_moves()) == 0
    def state(self):
        if self.legal_moves() == 0:
            if self.is_check():
                return "checkmate"
            else:
                return "stalemate"
        else:
            return "WHite to play" if self.turn == WHITE else "Black to play"
    def play_interactive(self):
        print("Game starting, to end game type 'exit'.")
        print(self)
        while True:
            moves = self.legal_moves()
            if len(moves) == 0:
                if self.is_check():
                    print("Checkmate.")
                else:
                    print("Stalemate.")
                break
            else:
                print("Possible moves:",*moves)
            move = input("Enter move in uci (or exit/undo/random): ")
            if move == "undo":
                self.undo_move()
            elif move == "exit":
                break
            elif move == "random":
                import random
                self.move(random.choice(moves))
            else:
                self.move(move)
            print(self)
    def fen(self):
        return self.position().fen()    
    def pgn(self):
        s=""
        if self.variant=="from_position":
            s+= '[Variant "From Position"]\n'
            if len(self.positions)>0:
                s += '[FEN "' + self.positions[0].fen() + '"]\n\n'
            else:
                s += '[FEN "' + self.position().fen() + '"]\n\n'
        for i, move in enumerate(self.moves):
            if i % 2 == 0:
                s += f"{i//2 + 1}. "
            s += str(move) + " "
        return s

def translate(object):
# Translate between python-chess and ramen-chess objects
    if isinstance(object, chess.Move):
        return Move.from_string(object.uci())
    elif isinstance(object, Move):
        return chess.Move.from_uci(object.uci())
    elif isinstance(object, Position):
        return chess.Board(object.fen())
    elif isinstance(object, Game):
        return translate(object.position())
    elif isinstance(object, chess.Board):
        return Game(object.fen())
    