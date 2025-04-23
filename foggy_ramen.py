from ramen_chess import *

class Engine:
    piece_values = { "pawn": 1, "knight": 3, "bishop": 3, "rook": 5, "queen": 9, "king": 0 }
    def __init__(self,position=None):
        if position is None:
            position = Position.starting()
        self.position = position
        self.game = Game(position)
    def material_score(self,color=None):
        if color is None:
            return self.material_score(WHITE) - self.material_score(BLACK)
        else:
            score=0
            for col in range(8):
                for row in range(8):
                    piece = self.game.board[col,row]
                    if piece is not None and piece.color == color:
                        score += self.piece_values[piece.type]
            return score
    def heuristical_score(self):
        state=self.game.state()
        if state == "checkmate":
            if self.game.turn == WHITE:
                return -9999
            else:
                return 9999
        elif state == "stalemate":
            return 0
        else:
            return self.material_score()
    def brute_force(self,depth=3):
        if depth == 0:
            return self.heuristical_score()
        moves = self.game.legal_moves()
        if len(moves) == 0:
            return self.heuristical_score()
        scores = []
        for move in moves:
            self.game.move(move)
            scores.append(self.brute_force(depth-1))
            self.game.undo_move()
        return max(scores) if self.game.turn == WHITE else min(scores)
    def best_move(self,depth=3,display=False):
        moves = self.game.legal_moves()
        scores = []
        for move in moves:
            if display:
                print(" " * depth + str(move))
            self.game.move(move)
            scores.append(self.brute_force(depth-1))
            self.game.undo_move()
        if self.game.turn == WHITE:
            best_index, best_score = max(enumerate(scores), key=lambda x: x[1])
        else:
            best_index, best_score = min(enumerate(scores), key=lambda x: x[1])
        return moves[best_index], best_score