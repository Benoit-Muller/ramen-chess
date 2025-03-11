import warnings
import copy


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
        return f"Square({self.col}, {self.row})"
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
    def __init__(self, start, end, promotion=None):
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
            return str(self.start)+str(self.end)
    def __repr__(self):
        return f"Move({self.start}, {self.end}, {self.promotion})"
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
        return isinstance(self.piece, King) and self.end.col - self.start.col == 2
    def is_long_castling(self):
        return isinstance(self.piece, King) and self.end.col - self.start.col == -2
    def is_castiling(self):
        return self.is_short_castling() or self.is_long_castling()
    def pseudo_algebraic(self):
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
            san += "=" + str(self.promotion)
        return san
    def interpret(self, board):
        self.piece = board[self.start]
        if self.piece is None:
            raise ValueError("No piece on start square.")
        self.capture = board[self.end]
        if self.capture is not None and self.capture.color == self.piece.color:
            raise ValueError("Cannot capture own piece.")
        self.is_en_passant = (
            isinstance(self.piece, Pawn) and 
            self.start.col != self.end.col and 
            board[self.end] is None
        )
        if self.is_en_passant:
            self.capture = board[self.end + (0, -1 if self.piece.color == WHITE else 1)]
        return self

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
                if game.en_passant_target() is not None:
                    if end == game.en_passant_target():
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
        if game.castling_rights()(self.color)["short"]:
            if game.board[5, row] is None and game.board[6, row] is None:
                moves.append(Move(start, start + (2, 0)))
        if game.castling_rights()(self.color)["long"]:
            if game.board[1, row] is None and game.board[2, row] is None and game.board[3, row] is None:
                moves.append(Move(start, start + (-2, 0)))
        return moves

class Board:
    def __init__(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]
    def __eq__(self, value):
        return isinstance(value, Board) and self.grid == value.grid
    def copy(self):
        new_board = Board()
        new_board.grid = [row.copy() for row in self.grid]
        return new_board
    def set_starting_position(self):
        self.clear()
        pieces= [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for col in range(8):
            self[col,0] = pieces[col](WHITE)
            self[col,1] = Pawn(WHITE)
            self[col,6] = Pawn(BLACK)
            self[col,7] = pieces[col](BLACK)

    def __getitem__(self, square):
        return self.grid[square[0]][square[1]]
    
    def __setitem__(self, square, piece):
        self.grid[square[0]][square[1]] = piece

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

class Game:
    def __init__(self):
        self.board = Board()
        self.board.set_starting_position()
        self.moves = []
    def __eq__(self, value):
        return isinstance(value, Game) and self.board == value.board and self.moves == value.moves
    def copy(self):
        new_game = Game()
        new_game.board = self.board.copy()
        new_game.moves = self.moves.copy()
        return new_game
    def move(self, move):
        move = self.board.move(move)
        self.moves.append(move)
        # TODO: check if move is legal, rigth turn, etc.
        return move
    def undo_move(self):
        return self.board.undo_move(self.moves.pop())
    def turn(self):
        return len(self.moves) % 2 == 0
    def castling_rights(self):
        # return dictionary with castling rights
        rights = {"white_short": True, "white_long": True, "black_short": True, "black_long": True}
        for move in self.moves:
            # white
            if move.start == Square(4, 0):
                rights["white_short"] = False
                rights["white_long"] = False
            elif move.start == Square(0, 0):
                rights["white_long"] = False
            elif move.start == Square(7, 0):
                rights["white_short"] = False
            # black
            elif move.start == Square(4, 7):
                rights["black_short"] = False
                rights["black_long"] = False
            elif move.start == Square(0, 7):
                rights["black_long"] = False
            elif move.start == Square(7, 7):
                rights["black_short"] = False
        def rights2(color):
            if color==WHITE:
                return {"short": rights["white_short"], "long": rights["white_long"]}
            else:
                return {"short": rights["black_short"], "long": rights["black_long"]}
        return rights2

    def en_passant_target(self):
        if len(self.moves) == 0:
            return None
        last_move = self.moves[-1]
        if isinstance(last_move.piece, Pawn) and abs(last_move.start.row - last_move.end.row) == 2:
            return last_move.end + (0, -1 if last_move.piece.color == WHITE else 1)
        return None
    def halfmove_clock(self):
        # return the number of halfmoves since the last capture or pawn move
        clock = 0
        for move in reversed(self.moves):
            if move.capture is not None or isinstance(move.piece, Pawn):
                break
            clock += 1
        return clock
    def fullmove_number(self):
        return len(self.moves) // 2 + 1
    def fen(self):
        s = ""
        for row in range(7, -1, -1):
            for col in range(8):
                piece = self.board[col, row]
                if piece is None:
                    s += "1"
                else:
                    s += piece.name
            s += "/"
        s = s[:-1]  # remove last slash
        s += " "
        s += "w" if self.turn() == WHITE else "b"
        s += " "
        rights = self.castling_rights()
        if rights(WHITE)["short"]:
            s += "K"
        if rights(WHITE)["long"]:
            s += "Q"
        if rights(BLACK)["short"]:
            s += "k"
        if rights(BLACK)["long"]:
            s += "q"
        if not s[-1] == " ":
            s += " "
        en_passant = self.en_passant_target()
        if en_passant is not None:
            s += str(en_passant)
        else:
            s += "-"
        s += " "
        s += str(self.halfmove_clock())
        s += " "
        s += str(self.fullmove_number())
        return s      
    def pgn(self):
        s = ""
        for i, move in enumerate(self.moves):
            if i % 2 == 0:
                s += f"{i//2 + 1}. "
            s += str(move) + " "
        return s
    def __str__(self):
        s_board = str(self.board)
        s_moves = self.pgn()
        s_state = "White to move." if self.turn() == WHITE else "Black to move."
        return s_moves + "\n" + s_board + "\n" + s_state

    def pseudo_legal_moves(self):
        moves = []
        for col in range(8):
            for row in range(8):
                piece = self.board[col, row]
                if piece is not None and piece.color == self.turn():
                    moves += piece.pseudo_legal_moves(self, Square(col, row))
        for i in range(len(moves)):
            moves[i].interpret(self.board)
        return moves
    
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
    def is_check(self):
        for move in self.pseudo_legal_moves():
            if isinstance(self.board[move.end], King):
                return True
        return False
    def pseudo_is_legal(self, move):
        move.interpret(self.board)
        assert move.piece.color == self.turn()
        self.move(move)
        next_moves = self.pseudo_legal_moves()
        for next_move in next_moves:
            if isinstance(next_move.capture, King):
                self.undo_move()
                return False
        if move.is_castiling():
            row=0 if move.piece.color==WHITE else 7
            if move.is_short_castling():
                for next_move in next_moves:
                    if next_move.end.row==row and next_move.end.col in [4,5,6]:
                        self.undo_move()
                        return False
            if move.is_long_castling():
                for next_move in next_moves:
                    if next_move.end.row==row and next_move.end.col in [4,3,2]:
                        self.undo_move()
                        return False
        self.undo_move()
        return True
    def legal_moves(self):
        moves = self.pseudo_legal_moves()
        return [move for move in moves if self.pseudo_is_legal(move)]
    def is_checkmate(self):
        return self.is_check() and len(self.legal_moves()) == 0
    def is_stalemate(self):
        return not self.is_check() and len(self.legal_moves()) == 0