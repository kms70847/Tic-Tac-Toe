import random
import threading
import time
from minmax import getBestMove, possibleMoves

#an intelligent computer player.
#uses minmax to get the best move.
class SmartCpuPlayer:
    def __init__(self, state, player):
        state.registerListener(self)
        self.state = state
        self.player = player
    def turnStarted(self, state, player):
        if player == self.player: #that's me!
            t = threading.Thread(None, self.makeMove)
            t.start()
    def makeMove(self):
        move, score = getBestMove(self.state, self.player, 3 - self.player)
        self.state.place(*move)