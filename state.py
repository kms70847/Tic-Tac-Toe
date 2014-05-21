from deferrer import deferred, Deferrer
from dispatcher import Dispatcher
import util

#remember to call checkDeferredCalls() to update the state
class State(Deferrer, Dispatcher):
	def __init__(self):
		self.width = 3
		self.height = 3
		Deferrer.__init__(self)
		Dispatcher.__init__(self)
		self.data = util.make2dArray(self.width, self.height, None)
		self.curPlayer = 1

	#listeners will receive the following calls:
	#turnStarted(state, player)
	#piecePlaced(state, player, x, y)
	#gameWon(state, player)
	
	#starts the game.
	def start(self):
		self.alert("turnStarted", self.curPlayer)

	def whoseTurn(self):
		return self.curPlayer
	
	def get(self, x, y):
		return self.data[x][y]
	
	def inRange(self, x, y):
		def isBetween(x,a,b):
			return x >= a and x <= b
		return isBetween(x, 0, self.width-1) and isBetween(y, 0, self.height-1)
	
	#hmm, might be a problem when the `place` call is deferred...
	#ex. a call to `place(0,0)` is in the queue, and `canPlace(0,0)` returns True anyway.
	#perhaps we can do some introspection on the pending calls queue...
	def canPlace(self, x, y):
		return self.inRange(x,y) and self.data[x][y] == None #and (not self.inRange(x,y+1) or self.data[x][y+1] != None)

	@deferred #new calls to `place` should be deferred until all listeners have been alerted.
	def _place(self, x, y):
		if not self.canPlace(x,y):
			raise Exception, "slot ({}, {}) is already occupied".format(x,y)
		self.data[x][y] = self.curPlayer
		self.alert("piecePlaced", self.curPlayer, x, y)
		if self.isGameOver():
			self.alert("gameWon", self.getWinner())
		else:
			self.curPlayer = 2 if self.curPlayer == 1 else 1
			self.alert("turnStarted", self.curPlayer)

	def place(self, x, y):
		self._place(x,y)
		if len(self.listeners) == 0: #if there's no listeners, we're free to perform the place right away
			self.checkDeferredCalls()

	def isBoardFull(self):
		for x in range(self.width):
			for y in range(self.height):
				if self.data[x][y] == None: return False
		return True
	def isGameOver(self):
		if self.isBoardFull(): return True
		return self.getWinner() != None
	def getWinner(self):
		amtInARowNeeded = 3
		
		#If all the points given have the same non-None state, returns that state.
		#returns None otherwise.
		def getMatchingState(points):
			if not all(self.inRange(x,y) for x,y in points):
				return None
			states = [self.get(x,y) for x,y in points]
			if len(set(states)) == 1 and states[0] != None:
				return states[0]
			return None
		deltas = [
			[(i, 0) for i in range(amtInARowNeeded)], #horizontal
			[(0, i) for i in range(amtInARowNeeded)], #vertical
			[(i, i) for i in range(amtInARowNeeded)], #increasing diagonal
			[(i,-i) for i in range(amtInARowNeeded)], #decreasing diagonal
		]
		for x in range(self.width):
			for y in range(self.height):
				for d in deltas:
					points = [(x+dx, y+dy) for dx,dy in d]
					state = getMatchingState(points)
					if state != None:
						return state
		return None
		
		def getByIdx(idx):
			idx -= 1
			x = idx / 3
			y = idx % 3
			return self.data[x][y]

		for strIdxs in "1 2 3, 4 5 6, 7 8 9, 1 4 7, 2 5 8, 3 6 9, 1 5 9, 3 5 7".split(", "):
			idxs = map(int, strIdxs.split())
			spots = map(getByIdx, idxs)
			if len(set(spots)) == 1 and spots[0] != None:
				return spots[0]
		return None

	#makes a copy of this State, but without the listeners
	def copy(self):
		ret = State()
		for i in range(self.width):
			for j in range(self.height):
				ret.data[i][j] = self.data[i][j]
		ret.curPlayer = self.curPlayer
		return ret
	def __eq__(self, other):
		if not isinstance(other, State):
			return False
		for i in range(self.width):
			for j in range(self.height):
				if self.data[i][j] != other.data[i][j]:
					return False
		if self.curPlayer != other.curPlayer:
			return False
		return True
	def __hash__(self):
		return hash(self.__repr__())
	def __repr__(self):
		return "\n".join("".join({1:'x', 2:'o', None: ' '}[self.data[i][j]] for i in range(self.width)) for j in range(self.height))

