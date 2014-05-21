from canvasPlayer import CanvasPlayer
from canvasView import *
from minmax import getBestMove, possibleMoves
from serialize import serialize, deserialize
from smartCpuPlayer import SmartCpuPlayer
from state import State
from stupidCpuPlayer import StupidCpuPlayer
from Tkinter import *

import time
import tkFileDialog
import tkMessageBox

class NoisyListener:
    def __init__(self, state):
        state.registerListener(self)
    def turnStarted(self, state, player):
        print "Player {}'s turn.".format(player)
    def piecePlaced(self, state, player, x, y):
        print "Player {} placed a piece at ({}, {}).".format(player, x, y)
        print state, "\n"
    def gameWon(self, state, player):
        if player == None:
            print "The game ended in a tie."
        else:
            print "Player {} won.".format(player)

class TopLevelWindow:
    def __init__(self, state):
        self.state = state
        self.root = Tk()
        self.root.wm_title("Tic Tac Toe")
        canvasSize = 400
        self.canvas = Canvas(self.root, width=canvasSize, height=canvasSize)
        self.canvas.pack()
        
        self.view = CanvasView(state, self.canvas)
        self.initListeners()
        
        self.initMenu()
    def start(self):
        #kickstart idle func
        self.idle()
        
        self.root.mainloop()

    def startGame(self, state):
        self.state = state
        self.view.setState(state)
        self.initListeners()
        self.state.start()
    
    def initListeners(self):
        NoisyListener(self.state)
        CanvasPlayer(self.state, 1, self.canvas)
        SmartCpuPlayer(self.state, 2)
        

    def initMenu(self):
        menubar = Menu(self.root)

        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="New",  command=self.newPressed)
        filemenu.add_command(label="Save", command=self.savePressed)
        filemenu.add_command(label="Load", command=self.loadPressed)
        filemenu.add_command(label="Exit", command=self.exitPressed)
        menubar.add_cascade(label="File", menu=filemenu)

        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Hint", command=self.hintPressed)
        helpmenu.add_command(label="About", command=self.aboutPressed)
        menubar.add_cascade(label="Help", menu=helpmenu)

        self.root.config(menu=menubar)
    def newPressed(self):
        self.startGame(State())
    def savePressed(self):
        filetypes = [('ttt files', '.ttt'), ('all files', '.*')]
        filename = tkFileDialog.asksaveasfilename(initialfile="savefile.ttt", filetypes=filetypes)
        if filename == "":
            return
        file = open(filename, "w")
        file.write(serialize(self.state))
        file.close()
    def loadPressed(self):
        filetypes = [('ttt files', '.ttt'), ('all files', '.*')]
        filename = tkFileDialog.askopenfilename(filetypes=filetypes)
        if filename == "":
            return
        data = open(filename).read()
        state = deserialize(data)
        self.startGame(state)
    def exitPressed(self):
        self.root.quit()
    def hintPressed(self):
        #possible enhancement: put this in a seperate thread so it doesn't lock up the interface.
        #it only has a noticeable delay for the very first move of the game, however, so NBD
        (x,y), _ = getBestMove(self.state, 1,2)
        self.view.throb(x,y)
    def aboutPressed(self):
        tkMessageBox.showinfo("About",  "Written by: Kevin Smiley\nThis work is licensed under a Creative Commons Attribution-ShareAlike 3.0 Unported License.")

    def idle(self):
        self.canvas.after(1000/600, self.idle)
        self.state.checkDeferredCalls()

s = State()
t = TopLevelWindow(s)

s.start()
t.start()