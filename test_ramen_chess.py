import unittest
from ramen_chess import *
import chess
import random

class TestPiece(unittest.TestCase):
    def setUp(self):
        self.piece = Knight(WHITE)
    def test_init(self):
        self.assertEqual(self.piece.color, WHITE)
        self.assertEqual(self.piece.type, 'knight')
        self.assertEqual(self.piece.name, 'N')
        self.assertEqual(self.piece.symbol, "♘")
    def test_str(self):
        self.assertEqual(str(self.piece), '♘')
    def test_repr(self):
        self.assertEqual(repr(self.piece), 'Knight(WHITE)')
    def test_eq(self):
        piece2 = Knight(WHITE)
        self.assertEqual(self.piece, piece2)
        piece3 = Knight(BLACK)
        self.assertNotEqual(self.piece, piece3)
    def test_from_string(self):
        piece = Piece.from_string("N")
        self.assertEqual(self.piece, piece)

class TestSquare(unittest.TestCase):
    def setUp(self):
        self.square = Square(4, 0)
    def test_init(self):
        self.assertEqual(self.square.col, 4)
        self.assertEqual(self.square.row, 0)
    def test_str(self):
        self.assertEqual(str(self.square), 'e1')
    def test_repr(self):
        self.assertEqual(repr(self.square), "Square.from_string('e1')")
    def test_eq(self):
        square2 = Square(4, 0)
        self.assertEqual(self.square, square2)
        square3 = Square(5, 0)
        self.assertNotEqual(self.square, square3)
    def test_add(self):
        diff = (-1, 1)
        square3 = self.square + diff
        self.assertEqual(square3, Square(3, 1))
    def test_getitem(self):
        self.assertEqual(self.square[0], 4)
        self.assertEqual(self.square[1], 0)
        with self.assertRaises(IndexError):
            _ = self.square[2]
    def test_from_string(self):
        square = Square.from_string("e1")
        self.assertEqual(self.square, square)

class TestMove(unittest.TestCase):
    def setUp(self):
        self.move = Move(Square(4, 1), Square(4, 3))
        self.piece=Pawn(WHITE)
    def test_init(self):
        for move in [self.move, Move("e2", "e4")]:
            self.assertEqual(move.start, Square(4, 1))
            self.assertEqual(move.end, Square(4, 3))
    def test_str(self):
        self.assertEqual(str(self.move), 'e2e4')
    def test_repr(self):
        self.assertEqual(repr(self.move), "Move('e2','e4')")
    def test_eq(self):
        move2 = Move(Square(4, 1), Square(4, 3))
        self.assertEqual(self.move, move2)
        move3 = Move(Square(4, 1), Square(5, 3))
        self.assertNotEqual(self.move, move3)
    def test_from_string(self):
        move = Move.from_string("e2e4")
        self.assertEqual(self.move, move)
    def test_is_short_castling(self):
        move1=Move.from_string("e1g1")
        move1.piece=King(WHITE)
        self.assertTrue(move1.is_short_castling())
        move2=Move.from_string("e1c1")
        move2.piece=King(WHITE)
        self.assertFalse(move2.is_short_castling())
        self.assertFalse(Move.from_string("e1f1").is_castling())
    def test_uci(self):
        self.assertEqual(self.move.uci(), "e2e4")

class TestBoard(unittest.TestCase):
    def setUp(self):
        self.fen= "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
        self.board = Board(self.fen)
    def test_init(self):
        self.assertEqual(self.board.grid[4][0], King(WHITE))
        self.assertEqual(Board().grid[4][0], None)
    def test_eq(self):
        self.assertEqual(self.board, self.board)
        board2 = Board(self.fen)
        self.assertEqual(self.board, board2)
        board3 = Board("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNQ")
        self.assertNotEqual(self.board, board3)
    def test_getitem(self):
        self.assertEqual(self.board[Square(4, 0)], King(WHITE))
        self.assertEqual(self.board[4,7], King(BLACK))
    def test_setitem(self):
        self.board[Square(4, 0)] = None
        self.assertEqual(self.board[Square(4, 0)], None)
        self.board[Square(4, 0)] = King(WHITE)
        self.assertEqual(self.board[Square(4, 0)], King(WHITE))
    def test_str(self):
        self.assertEqual(self.board.fen(), self.fen)
    def test_repr(self):
        self.assertEqual(repr(self.board), "Board('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR')")
    def test_copy(self):
        board2 = self.board.copy()
        self.assertEqual(self.board, board2)
        self.assertIsNot(self.board, board2)
    def test_move(self):
        move = Move("e2", "e4")
        self.board.move(move)
        self.assertIsNone(self.board[Square("e","2")])
        self.assertEqual(self.board[Square("e","4")], Pawn(WHITE))
    def test_fen(self):
        self.assertEqual(self.board.fen(), self.fen)

class TestPosition(unittest.TestCase):
    def setUp(self):
        self.fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        self.position = Position.from_fen(self.fen)
    def test_init(self):
        self.assertEqual(self.position.board, Board(self.position.board.fen()))
        self.assertEqual(self.position.turn, WHITE)
        self.assertEqual(self.position.castling_rights["white_short"], True)
        self.assertIs(self.position.en_passant_target, None)
        self.assertEqual(self.position.halfmove_clock, 0)
        self.assertEqual(self.position.fullmove_number, 1)
    def test_str(self):
        self.assertEqual(str(self.position), self.fen)
    def test_eq(self):
        position2 = Position.from_fen(self.fen)
        self.assertEqual(self.position, position2)
        position3 = Position.from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 2")
        self.assertNotEqual(self.position, position3)
    def test_copy(self):
        position2 = self.position.copy()
        self.assertEqual(self.position, position2)
        self.assertIsNot(self.position, position2)
    def fen(self):
        self.assertEqual(self.position.fen(), self.fen)

class TestGame(unittest.TestCase):
    def setUp(self):
        self.fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        self.game = Game(self.fen)
    def test_init(self):
        self.assertEqual(self.game.position(), Position.from_fen(self.fen))
    def test_move(self):
        move = Move("e2", "e4")
        self.game.move(move)
        self.assertEqual(self.game.board[Square("e","4")], Pawn(WHITE))
        self.assertIsNone(self.game.board[Square("e","2")])
        self.game.undo_move()
        self.assertEqual(self.game.fen(), self.fen)
    def test_move_generation(self):
        for repeat in range(10):
            game = Game()
            for i in range(200):
                p_board = chess.Board(game.fen())
                fen = game.fen()
                p_fen = p_board.fen(en_passant="fen")
                self.assertEqual(fen, p_fen)
                moves = game.legal_moves()
                moves_uci = {move.uci() for move in moves}
                p_moves_uci = {move.uci() for move in p_board.legal_moves}
                self.assertEqual(moves_uci, p_moves_uci)
                if len(moves) == 0:
                    break
                else:
                    game.move(random.choice(moves))

if __name__ == "__main__":
    unittest.main()