import random
import threading
import time

class CanvasPlayer:
    def __init__(self, state, player, canvas):
        self.state = state
        self.player = player
        self.canvas = canvas
        self.canvas.bind("<Button-1>", self.clicked)
    def clicked(self, e):
        if self.state.whoseTurn() != self.player or self.state.isGameOver():
            return
        x = e.x * self.state.width / int(self.canvas.cget("width"))
        y = e.y * self.state.height/ int(self.canvas.cget("height"))
        
        if self.state.canPlace(x,y):
            self.state.place(x,y)