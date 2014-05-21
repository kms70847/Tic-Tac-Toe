import random
import threading
import time

#a not-so-intelligent computer player.
#when its turn comes, it waits three seconds, and chooses a random unoccupied spot.
class StupidCpuPlayer:
    def __init__(self, state, player):
        state.registerListener(self)
        self.state = state
        self.player = player
    def turnStarted(self, state, player):
        if player == self.player: #that's me!
            t = threading.Thread(None, self.makeMove)
            t.start()
    def makeMove(self):
        time.sleep(0.5)
        possibleMoves = []
        for i in range(self.state.width):
            for j in range(self.state.height):
                if self.state.canPlace(i,j):
                    possibleMoves.append((i,j))
        i,j = random.choice(possibleMoves)
        self.state.place(i,j)