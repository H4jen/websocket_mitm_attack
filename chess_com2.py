

#import keyboard
import subprocess
import re
import curses
import os
from curses import wrapper
import json

from pystockfish import *

DEBUG_LEVEL = "OFF" #Debug levels are:  Off, MSG, MOVES
SHOW_BEST_MOVE = "ON"


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

class InMessage:
    def __init__(self, messy,direction):
        self.move_flag = False
        l=re.compile("\"")
        self.msg=l.split(messy)
        self.direction = direction
        if (len(self.msg) <4) :
            self.msg = " "
            return
        if (len(self.msg) > 60):
       		if(self.msg[55] == "moves"):

                        moves=self.msg[57]
                        if(DEBUG_LEVEL == "MOVES"): 
                                stdscr.addstr(7,0,"Moves string chess.com is:" + moves)

                        moves = re.findall('..',moves)
                        if(len(moves) > 1):
                                moves_uci = []
                                for movee in moves:
                                        move_string = ''
                                        for elem in movee:
                                                move_string = move_string + chess_com_notation_to_uci(elem)
                                        moves_uci.append(move_string)
                                if(len(moves_uci) == 1):
                                        print("We have a NEW game")
                                if(DEBUG_LEVEL == "MOVES"): 
                                        stdscr.addstr(8,0,"Moves string UCI is:" + "".join(moves_uci))
                                stocky.newgame()
                                stocky.setposition(moves_uci)
                                if (SHOW_BEST_MOVE == "ON"):
                                        stdscr.move(10,0)
                                        stdscr.clrtoeol()
                                        stdscr.addstr(10,0,json.dumps(stocky.bestmove()))
                                else :
                                        stdscr.move(10,0)
                                        stdscr.clrtoeol()
                                        stdscr.addstr(10,0,"Best move is OFF use b key to toggle")


p = subprocess.Popen(["mitmdump", "-s", "websocket_messages.py"],universal_newlines=True, stdout=subprocess.PIPE)
stocky = Engine(depth=20)

stdscr = curses.initscr()
curses.noecho()
stdscr.nodelay(1) # set getch() non-blocking

stdscr.addstr(0,0,"To use press the below keys")
stdscr.addstr(2,0,"\"q\" to exit...")
stdscr.addstr(3,0,"\"b\" to toggle bestmove...")
line = 1

try:
    message_dir = "none"
    while True:
       c = stdscr.getch()
       if c == ord('b'):
           if (SHOW_BEST_MOVE == "ON"): SHOW_BEST_MOVE = "OFF"
           else : SHOW_BEST_MOVE = "ON"
       elif c == ord('q'): break

       line=p.stdout.readline()
       if not line:
           continue
       #Print evrything received. If debuglevel = high
       if (DEBUG_LEVEL== "MSG"): print(line)

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

    curses.endwin()
    p.kill()

