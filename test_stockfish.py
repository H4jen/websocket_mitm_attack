from pystockfish import *

deep = Engine(depth=20)
#deep.setposition(['e2e4'])
#print(deep.bestmove())

#deep.setposition(['e2e4','e7e5'])
#print(deep.bestmove())

#deep.setposition(['e2e4','e7e5', 'h2h4'])
#print(deep.bestmove())

deep.setposition(['e2e4','e7e5', 'h2h4', 'a7a5'])
print(deep.bestmove())
#

#{'info': 'info depth 10 seldepth 2 score cp 40 nodes 4230 nps 1057500 time 4 multipv 1 pv g1f3 g8f6 b1c3 b8c6 f1b5 f8d6 e1g1 e8g8 d2d4 e5d4 f3d4 a7a6', 'ponder': 'g8f6', 'move': 'g1f3'}  

#shallow = Engine(depth=10)
#match = Match(engines={'deep': deep, 'shallow':shallow})
#match.run()
#'deep'
