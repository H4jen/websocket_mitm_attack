import keyboard
import subprocess
import re

from pystockfish import *


def chess_com_notation_to_uci(chess_com_notation):
	switcher = {
		"a": "a1",
		"b": "b1",
		"c": "c1",
		"d": "d1",
		"e": "e1",
		"f": "f1",
		"g": "g1",
		"h": "h1",
		"i": "a2",
		"j": "b2",
		"k": "c2",
		"l": "d2",
		"m": "e2",
		"n": "f2",
		"o": "g2",
		"p": "h2",
		"q": "a3",
		"r": "b3",
		"s": "c3",
		"t": "d3",
		"u": "e3",
		"v": "f3",
		"w": "g3",
		"x": "h3",
		"y": "a4",
		"z": "b4",
		"A": "c4",
		"B": "d4",
		"C": "e4",
		"D": "f4",
		"E": "g4",
		"F": "h4",
		"G": "a5",
		"H": "b5",
		"I": "c5",
		"J": "d5",
		"K": "e5",
		"L": "f5",
		"M": "g5",
		"N": "h5",
		"O": "a6",
		"P": "b6",
		"Q": "c6",
		"R": "d6",
		"S": "e6",
		"T": "f6",
		"U": "g6",
		"V": "h6",
		"W": "a7",
		"X": "b7",
		"Y": "c7",
		"Z": "d7",
		"0": "e7",
		"1": "f7",
		"2": "g7",
		"3": "h7",
		"4": "a8",
		"5": "b8",
		"6": "c8",
		"7": "d8",
		"8": "e8",
		"9": "f8",
		"!": "g8",
		"?": "h8",
	}
	return switcher.get(chess_com_notation,"error")


class chess_move:
    def __init__(self,move_nr,uci,san,fen,turn):
            self.move_nr=move_nr
            self.uci = uci
            self.san = san
            self.fen = fen
            self.turn = turn

class chess_game:
    def __init__(self):
        self.moves_uci = []
        self.moves_san = []
        self.moves_fen = []

    def reinit(self):
        self.moves_uci.clear()
        self.moves_san.clear()
        self.moves_fen.clear()

    def add_move(self,move):
        self.moves_uci.append(move.uci)
        self.moves_san.append(move.san)
        self.moves_fen.append(move.fen)
                

# input: "t":"move","v":29,"d":{"uci":"a4c6","san":"Qxc6","fen":"r2qk2r/2pn1ppp/ppQp4/3Pp1b1/4P3/2N2P2/PP2N1PP/R4RK1","ply":29,"clock":{"white":536.65,"black":540.66,"lag":27}}
# input: "t":"move","v":30,"d":{"uci":"a8b8","san":"Rb8","fen":"1r1qk2r/2pn1ppp/ppQp4/3Pp1b1/4P3/2N2P2/PP2N1PP/R4RK1","ply":30,"dests":{"a1":"b1c1d1e1","f1":"f2e1d1c1b1","c6":"c7c5c4b6d6b7a8d7b5a4","g2":"g3g4","g1":"h1f2","f3":"f4","b2":"b3b4","e2":"d4f4c1g3","c3":"b5b1d1a4","a2":"a3a4","h2":"h3h4"},"clock":{"white":536.65,"black":535.92,"lag":3}}
#constructor takes move messages and sorts into parameters

#['{', 'data', ':{', 'game', ':{', 'id', ':4756447454,', 'status', ':', 'in_progress', ',', 'players', ':[{', 'uid', ':', 'hajen2', ',', 'status', ':', 'playing', ',', 'userclass'17, ':', 'GGL'18, ','19, 'lag'20, ':1,'21, 'lagms'22, ':110,'23, 'gid'24, ':4756447454},{',25 'uid'26, ':'27, 'Guitouni'28, ',', 'status'29, ':', 'playing'30, ',', 'userclass'31, ':', 'GGL'32, ',', 'lag33', ':1,'34, 'lagms35', ':116,', 'gid', ':4756447454}],', 'reason', ':', 'movemade', ',', 'seq', ':6,', 'moves', ':', 'lBZJcD5Qmu!T', ',', 'clocks', ':[5965,5922],', 'draws', ':[],', 'squares', ':[0,0]},', 'tid', ':', 'GameState', ',', 'sid', ':', 'gserv', '},', 'channel', ':', '/game/4756447454', '}']
#  0     1       2     3      4     5      6               7        8       9           10    11         12     13           14       
class InMessage:
    def __init__(self, messy,direction):
        self.move_flag = False
        l=re.compile("\"")
        self.msg=l.split(messy)
        self.direction = direction
        if (len(self.msg) <4) :
            self.msg = " "
            return
        #print(self.msg)
        if (len(self.msg) > 60):
       		#print(self.msg)
       		if(self.msg[55] == "moves"):
                        moves=self.msg[57]
       			#print("Moves are:" +  moves)
                        #put moves in string array
                        moves = re.findall('..',moves)
                        #print(moves)
                        if(len(moves) > 1):
                                moves_uci = []
                                for movee in moves:
                                        move_string = ''
                                        for elem in movee:
                                                move_string = move_string + chess_com_notation_to_uci(elem)
                                        moves_uci.append(move_string)
                                #print(moves_uci)
                                #print(len(moves_uci))
				#print("Move is:" + move_string)
       				#move_uci = chess_com_notation_to_uci(move_string[0]) + chess_com_notation_to_uci(move_string[1])
       				#print("Move in uci is:" + move_uci)
       				#move_nmbr_string = self.msg[54]
       				#move_nmbr_string=move_nmbr_string.replace(':','')
       				#move_nmbr_string=move_nmbr_string.replace(',','')
       				#move_nr=str(move_nmbr_string)
       				#print("Move number = " + move_nr)
                                if(len(moves_uci) == 1):
					#game.reinit()
	                                #stocky.newgame()
                                        print("We have a NEW game")
				#game.reinit()
				#stocky = Engine(depth=20)
                                stocky = Engine(depth=20)
                                stocky.newgame()
                                stocky.setposition(moves_uci)
                                #print(moves_uci)
                                print(stocky.bestmove())
       				#uci = move_uci
       				#san = "empty"
       				#fen = "empty"
       				#self.move = chess_move(move_nr,uci,san,fen,"w")
       				#self.move_flag = True
            #if((move_nr % 2) == 0):
            #    self.move_turn = "b"
            #else:
            #    self.move_turn = "w"
            #self.move = chess_move(move_nr,uci,san,fen,self.move_turn)
            #self.move_flag = True
#['', 't', ':', 'move', ',', 'd', ':{', 'u', ':', 'e2e4', ',', 'l', ':31,', 'a', ':1}']
#['', 't', ':', 'ack', ',', 'd', ':1']
#['', 't', ':', 'move', ',', 'v', ':1,', 'd', ':{', 'uci', ':', 'e2e4', ',', 'san', ':', 'e4', ',', 'fen', ':', 'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR', ',', 'ply', ':1,', 'clock', ':{', 'white', ':600,', 'black', ':600}}']
#['', 't', ':', 'move', ',', 'v', ':2,', 'd', ':{', 'uci', ':', 'e7e5', ',', 'san', ':', 'e5', ',', 'fen', ':', 'rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR', ',', 'ply', ':2,', 'dests', ':{', 'f1', ':

#game = chess_game()
#stocky = Engine(depth=20)
p = subprocess.Popen(["mitmdump", "-s", "websocket_messages.py"],universal_newlines=True, stdout=subprocess.PIPE)

try:
    message_dir = "none"
    while True:
       line=p.stdout.readline()
       if not line:
           continue
       #filter out incoming message. And send to parser
       if isinstance(line, str):
           if "<- WebSocket 1 message <-" in line:
               message_dir = "input"
               continue
           elif "-> WebSocket 1 message ->" in line:
               message_dir ="output"
               continue
           else:
             if (line[0] == "["):
                 crop_line=line[line.find("[")+1:line.rfind("]")]
                 if len(crop_line) == 0:
                 	continue
                 else:
                       rx_msg = InMessage(crop_line,message_dir)
                       #print(crop_line)
                       #if (rx_msg.move_flag):
                           #    print(rx_msg.move_turn + " " + str(rx_msg.move.move_nr) + ": " + rx_msg.move.san)
                           #We have a legit chess move.
                           # 1) Check is this is first move (flush old game) and start new game + re-init engine.
                           # 2) Send move to chess engine
                           # 3) Display made move and "best" wanted engine move 
                           # 4) let stocky go
                           # 4) store move made in game
                           #if(rx_msg.move.move_nr == 1): #re-init game class
                           #    print("************* RE-INIT *************")
                           #    game.reinit()
                           #    stocky.newgame()
                               #stocky.setfenposition(self,"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
                               #filter out som special moves and change notation
                           #if(rx_msg.move.san == "O-O"):
                           #    if(rx_msg.move.turn == "w"):
                           #        print("Short castle white")
                           #        rx_msg.move.uci = "e1g1"
                           #    else:
                           #        print("Short castle black")
                           #        rx_msg.move.uci = "e8g8"
                           #if(rx_msg.move.san == "O-O-O"):
                           #    if(rx_msg.move.turn == "w"):
                           #        print("Long castle white")
                           #        rx_msg.move.uci = "e1c1"
                           #    else:
                           #        print("Long castle black") 
                           #        rx_msg.move.uci = "e8c8"
                           #game.add_move(rx_msg.move)
                           #stocky.setposition(game.moves_uci)
                           #print(game.moves_uci)
                          # stocky.isready()
                          # print(stocky.bestmove())

except KeyboardInterrupt:
    pass
