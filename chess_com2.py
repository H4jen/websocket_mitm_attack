#import keyboard
import subprocess
import re
import curses
import os
from curses import wrapper
import json

from pystockfish import *

DEBUG_LEVEL = "OFF" #Debug levels are:  Off, MSG, MOVES
SHOW_BEST_MOVE = "OFF"
SHOW_SCORE_OF_MOVE = "ON"
SHOW_IF_BEST_MOVE_WAS_PLAYED = "ON"
LAST_BEST_MOVE = "EMPTY"
CURRENT_BEST_MOVE = "EMPTY"
CURRENT_SCORE = "EMPTY"
#TRIGGER_HAPPY = 1

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
        global LAST_BEST_MOVE
        self.move_flag = False
        l=re.compile("\"")
        self.msg=l.split(messy)
        self.direction = direction
        if (len(self.msg) <4) :
            self.msg = " "
            return
        if (len(self.msg) > 60):
       		if(self.msg[55] == "moves"):
                        #new move. current is now last best move
                        #LAST_BEST_MOVE = CURRENT_BEST_MOVE
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
                                        #stdscr.addstr(17,0,"Latest move is:" + chess_com_notation_to_uci(moves_uci[-1])
                                if(len(moves_uci) == 1):
                                        print("We have a NEW game")
                                if(DEBUG_LEVEL == "MOVES"): 
                                        stdscr.addstr(8,0,"Moves string UCI is:" + "".join(moves_uci))
                                stocky.newgame()
                                stocky.setposition(moves_uci)
                                stocky_result = stocky.bestmove()
                                if(len(stocky_result) == 2):
                                        CURRENT_BEST_MOVE = stocky_result["move"]
                                        CURRENT_SCORE = stocky_result["Score"]
                                        if (SHOW_BEST_MOVE == "ON"):
                                             stdscr.move(10,0)
                                             stdscr.clrtoeol()
                                             stdscr.addstr(10,0,"Current best move: " + CURRENT_BEST_MOVE)
                                             stdscr.move(11,0)
                                             stdscr.clrtoeol()
                                             stdscr.addstr(11,0,"Current score is : " + CURRENT_SCORE)
                                        else :
                                             stdscr.move(11,0)
                                             stdscr.clrtoeol()
                                             stdscr.move(10,0)
                                             stdscr.clrtoeol()
                                             stdscr.addstr(10,0,"Best move is OFF use b key to toggle")

                                        if (SHOW_IF_BEST_MOVE_WAS_PLAYED == "ON"):
                                             stdscr.move(13,0)
                                             stdscr.clrtoeol()
                                             if(LAST_BEST_MOVE == moves_uci[-1]):
                                                  stdscr.addstr(13,0,"$$$$$  BEAST MOVE WAS PLAYED!!! $$$$$")
                                             else :
                                                  stdscr.addstr(13,0,"Best move was:" + LAST_BEST_MOVE)
                                             LAST_BEST_MOVE = CURRENT_BEST_MOVE
                                        else :
                                             stdscr.move(13,0)
                                             stdscr.clrtoeol()
                                             stdscr.addstr(13,0,"Best score shout is OFF use s key to toggle")

                                        if (SHOW_SCORE_OF_MOVE == "ON"):
                                             stdscr.move(15,0)
                                             stdscr.clrtoeol()
                                             stdscr.addstr(15,0,"Current score is : " + CURRENT_SCORE)
                                        else :
                                             stdscr.move(15,0)
                                             stdscr.clrtoeol()
                                             stdscr.addstr(15,0,"Score is OFF use d key to toggle")

p = subprocess.Popen(["mitmdump", "-s", "websocket_messages.py"],universal_newlines=True, stdout=subprocess.PIPE)
stocky = Engine(depth=20)

stdscr = curses.initscr()
curses.noecho()
stdscr.nodelay(1) # set getch() non-blocking

stdscr.addstr(0,0,"To use press the below keys")
stdscr.addstr(2,0,"\"q\" to exit...")
stdscr.addstr(3,0,"\"b\" to toggle bestmove...")
stdscr.addstr(4,0,"\"s\" to toggle best move SHOUT!!...")
stdscr.addstr(4,0,"\"d\" to toggle score view!!...")
line = 1

try:
    message_dir = "none"
    LAST_BEST_MOVE = "EMPTY"    
    while True:
       c = stdscr.getch()
       if c == ord('b'):
           if (SHOW_BEST_MOVE == "ON"): SHOW_BEST_MOVE = "OFF"
           else : SHOW_BEST_MOVE = "ON"
       if c == ord('s'):
           if (SHOW_IF_BEST_MOVE_WAS_PLAYED == "ON"): SHOW_IF_BEST_MOVE_WAS_PLAYED = "OFF"
           else : SHOW_IF_BEST_MOVE_WAS_PLAYED = "ON"
       if c == ord('d'):
           if (SHOW_SCORE_OF_MOVE == "ON"): SHOW_SCORE_OF_MOVE = "OFF"
           else : SHOW_SCORE_OF_MOVE = "ON"

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

finally:
    curses.endwin()
    p.kill()

