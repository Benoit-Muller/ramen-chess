from importlib import reload
import ramen_chess
import foggy_ramen
reload(ramen_chess)
reload(foggy_ramen)
from ramen_chess import *
from foggy_ramen import *

engine=Engine()
print(engine.game)
move=engine.best_move()