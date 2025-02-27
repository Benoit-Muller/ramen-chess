import chess
import importlib

board = chess.Board()
board.set_starting_position()
board.move("f2f3")
board.move("e7e6")
board.move("g2g4")
print("fastest mate:")
board.move("d8h4",show=True)
moves = board.pseudo_legal_moves(chess.WHITE)
print(*moves)