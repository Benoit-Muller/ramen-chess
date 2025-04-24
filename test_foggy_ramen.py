from importlib import reload
import ramen_chess
import foggy_ramen
reload(ramen_chess)
reload(foggy_ramen)
from ramen_chess import *
from foggy_ramen import *

fen="r3kb1r/ppP2ppp/5n2/4q3/3n4/2NBB3/PPP1NPbP/R2QK2R b KQkq - 5 11"
engine=Engine(Position.from_fen(fen))
print(engine.game.board)
move,score=engine.best_move(depth=2,display=True)
print("Best move:", move)