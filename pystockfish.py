"""
    pystockfish
    ~~~~~~~~~~~~~~~

    Wraps the Stockfish chess engine.  Assumes stockfish is
    executable at the root level.

    Built on Ubuntu 12.1 tested with Stockfish 120212.
    
    :copyright: (c) 2013 by Jarret Petrillo.
    :license: GNU General Public License, see LICENSE for more details.
"""

import re
import subprocess
from random import randint
MAX_MOVES = 200
UCI_MOVE_REGEX = "[a-h]\d[a-h]\d[qrnb]?"
PV_REGEX = " pv (?P<move_list>{0}( {0})*)".format(UCI_MOVE_REGEX)


class Match:
    """
    The Match class setups a chess match between two specified engines.  The white player
    is randomly chosen.

    deep_engine = Engine(depth=20)
    shallow_engine = Engine(depth=10)
    engines = {
        'shallow': shallow_engine,
        'deep': deep_engine,
        }

    m = Match(engines=engines)

    m.move() advances the game by one move.

    m.run() plays the game until completion or 200 moves have been played,
    returning the winning engine name.
    """

    def __init__(self, engines):
        random_bin = randint(0, 1)
        self.white = list(engines.keys())[random_bin]
        self.black = list(engines.keys())[not random_bin]
        self.white_engine = engines.get(self.white)
        self.black_engine = engines.get(self.black)
        self.moves = []
        self.white_engine.newgame()
        self.black_engine.newgame()
        self.winner = None
        self.winner_name = None

    def move(self):
        """
        Advance game by single move, if possible.

        @return: logical indicator if move was performed.
        """
        if len(self.moves) == MAX_MOVES:
            return False
        elif len(self.moves) % 2:
            active_engine = self.black_engine
            active_engine_name = self.black
            inactive_engine = self.white_engine
            inactive_engine_name = self.white
        else:
            active_engine = self.white_engine
            active_engine_name = self.white
            inactive_engine = self.black_engine
            inactive_engine_name = self.black
        active_engine.setposition(self.moves)
        movedict = active_engine.bestmove()
        bestmove = movedict.get('move')
        info = movedict.get('info')
        ponder = movedict.get('ponder')
        self.moves.append(bestmove)

        if info["score"]["eval"] == "mate":
            matenum = info["score"]["value"]
            if matenum > 0:
                self.winner_engine = active_engine
                self.winner = active_engine_name
            elif matenum < 0:
                self.winner_engine = inactive_engine
                self.winner = inactive_engine_name
            return False

        if ponder != '(none)':
            return True

    def run(self):
        """
        Returns the winning chess engine or "None" if there is a draw.
        """
        while self.move():
            pass
        return self.winner


class Engine(subprocess.Popen):
    """
    This initiates the Stockfish chess engine with Ponder set to False.
    'param' allows parameters to be specified by a dictionary object with 'Name' and 'value'
    with value as an integer.

    i.e. the following explicitly sets the default parameters
    {
        "Contempt Factor": 0,
        "Min Split Depth": 0,
        "Threads": 1,
        "Hash": 16,
        "MultiPV": 1,
        "Skill Level": 20,
        "Move Overhead": 30,
        "Minimum Thinking Time": 20,
        "Slow Mover": 80,
    }

    If 'rand' is set to False, any options not explicitly set will be set to the default
    value.

    -----
    USING RANDOM PARAMETERS
    -----
    If you set 'rand' to True, the 'Contempt' parameter will be set to a random value between
    'rand_min' and 'rand_max' so that you may run automated matches against slightly different
    engines.
    """
    staticScore = -999
    prevStaticScore = -999
    scoreDiff = -999
    def __init__(self, depth=2, ponder=True, param={}, rand=False, rand_min=-10, rand_max=10):
        subprocess.Popen.__init__(self,
                                  'stockfish',
                                  universal_newlines=True,
                                  stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, )
        self.depth = str(depth)
        self.ponder = ponder
        self.put('uci')
        if not ponder:
            self.setoption('Ponder', False)

        base_param = {
            "Write Debug Log": "false",
            "Contempt Factor": 0,  # There are some stockfish versions with Contempt Factor
            "Contempt": 0,  # and others with Contempt. Just try both.
            "Min Split Depth": 0,
            "Threads": 1,
            "Hash": 16,
            "MultiPV": 1,
            "Skill Level": 20,
            "Move Overhead": 30,
            "Minimum Thinking Time": 20,
            "Slow Mover": 80,
            "UCI_Chess960": "false",
        }

        if rand:
            base_param['Contempt'] = randint(rand_min, rand_max),
            base_param['Contempt Factor'] = randint(rand_min, rand_max),

        base_param.update(param)
        self.param = base_param
        for name, value in list(base_param.items()):
            self.setoption(name, value)

    def newgame(self):
        """
        Calls 'ucinewgame' - this should be run before a new game
        """
        self.put('ucinewgame')
        self.isready()

    def put(self, command):
        self.stdin.write(command + '\n')
        self.stdin.flush()

    def flush(self):
        self.stdout.flush()

    def setoption(self, optionname, value):
        self.put('setoption name %s value %s' % (optionname, str(value)))
        stdout = self.isready()
        if stdout.find('No such') >= 0:
            print("stockfish was unable to set option %s" % optionname)

    def setposition(self, moves=[]):
        """
        Move list is a list of moves (i.e. ['e2e4', 'e7e5', ...]) each entry as a string.  Moves must be in full algebraic notation.
        """
        self.put('position startpos moves %s' % Engine._movelisttostr(moves))
        self.isready()

    def setfenposition(self, fen):
        """
        set position in fen notation.  Input is a FEN string i.e. "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
        """
        self.put('position fen %s' % fen)
        self.isready()

    def go(self):
        self.put('go depth %s' % self.depth)

    @staticmethod
    def _movelisttostr(moves):
        """
        Concatenates a list of strings.

        This is format in which stockfish "setoption setposition" takes move input.
        """
        return ' '.join(moves)

    def bestmove(self):
        """
        Get proposed best move for current position.

        @return: dictionary with 'move', 'ponder', 'info' containing best move's UCI notation,
        ponder value and info dictionary.
        info depth 31 seldepth 55 multipv 1 score cp -501 nodes 42307349 nps 1866637 hashfull 999 tbhits 0 time 22665 pv b5c4 d3c4 d5b4 a1e1 h8e8 f3h4 f5f4 g3f4 d7b6 c4f7 b6d5 h4f5 b4d3 f5e7 e8e7 e1e7 d5e7 f7e7 d3f4 e7f8 c8b7 f8f4 a8d8 f2f3 d8d7 f4f8 b7c7 f8c5 a7a6 g1f2 c7b7 c5e5 c6d5 f2e3 b7b6 e5e8 d7c7 e8f8 d5c6 f8d6 c7d7 d6c5 b6b7 e3f2 b7c7 c5f8 c7b6
	bestmove b5c4 ponder d3c4

        """
        self.go()
        last_info = ""
        staticScore=999
        #prevStaticScore
        while True:
            text = self.stdout.readline().strip()
            split_text = text.split(' ')
            #print(text)
            if split_text[0] == "info": #find balance score
                if ("cp" in split_text):
                         index_cp = split_text.index("cp") #last_info = Engine._bestmove_get_info(text)
                         if len(split_text) > (index_cp+1):
                                  #print(split_text[index_cp+1])
                                  staticScore = split_text[index_cp+1]
                                  #print(staticScore)

            if split_text[0] == "bestmove":   #ponder = None if len(split_text[0]) < 3 else split_text[3]
                return {'move': split_text[1],
                        'Score': staticScore}

    @staticmethod
    def _bestmove_get_info(text):
        """
        Parse stockfish evaluation output as dictionary.

        Examples of input:

        "info depth 2 seldepth 3 multipv 1 score cp -656 nodes 43 nps 43000 tbhits 0 \
        time 1 pv g7g6 h3g3 g6f7"

        "info depth 10 seldepth 12 multipv 1 score mate 5 nodes 2378 nps 1189000 tbhits 0 \
        time 2 pv h3g3 g6f7 g3c7 b5d7 d1d7 f7g6 c7g3 g6h5 e6f4"
        """
        #result_dict = Engine._get_info_pv(text)
        #print("info info:")
        print(text)
	#search = re.search(pattern="score (?P<eval>\w+) (?P<value>-?\d+)", string=test)
        #print(result_dict)
        #result_dict.update(Engine._get_info_score(text))

        #single_value_fields = ['depth', 'seldepth', 'multipv', 'nodes', 'nps', 'tbhits', 'time']
        #for field in single_value_fields:
        #    result_dict.update(Engine._get_info_singlevalue_subfield(text, field))

        #return result_dict

    @staticmethod
    def _get_info_singlevalue_subfield(info, field):
        """
        Helper function for _bestmove_get_info.

        Extracts (integer) values for single value fields.
        """
        search = re.search(pattern=field + " (?P<value>\d+)", string=info)
        return {field: int(search.group("value"))}

    @staticmethod
    def _get_info_score(info):
        """
        Helper function for _bestmove_get_info.

        Example inputs:

        score cp -100        <- engine is behind 100 centipawns
        score mate 3         <- engine has big lead or checkmated opponent
        """
        search = re.search(pattern="score (?P<eval>\w+) (?P<value>-?\d+)", string=info)
        #print ({"score": {"eval": search.group("eval"), "value": int(search.group("value"))}})
        return {"score": {"eval": search.group("eval"), "value": int(search.group("value"))}}

    @staticmethod
    def _get_info_pv(info):
        """
        Helper function for _bestmove_get_info.

        Extracts "pv" field from bestmove's info and returns move sequence in UCI notation.
        """
        search = re.search(pattern=PV_REGEX, string=info)
        return {"pv": search.group("move_list")}

    def isready(self):
        """
        Used to synchronize the python engine object with the back-end engine.  Sends 'isready' and waits for 'readyok.'
        """
        self.put('isready')
        while True:
            text = self.stdout.readline().strip()
            if text == 'readyok':
                return text
