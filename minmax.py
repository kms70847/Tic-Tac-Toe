def memoize(fn):
	answers = {}
	def memFn(*args):
		key = tuple(args)
		if key not in answers:
			answers[key] = fn(*args)
		return answers[key]
	return memFn

def turnsPlayed(state):
	turns = 0
	for x in range(state.width):
		for y in range(state.height):
			if state.get(x,y) != None:
				turns += 1
	return turns

def value(state, curPlayer, otherPlayer):
	maxPossibleTurnsPlayed = state.width*state.height
	winner = state.getWinner()
	if winner == curPlayer:
		return 100 * (maxPossibleTurnsPlayed - turnsPlayed(state))
	if winner == otherPlayer:
		return -100 * (maxPossibleTurnsPlayed - turnsPlayed(state))
	return 0

def possibleMoves(state):
	for i in range(state.width):
		for j in range(state.height):
			if state.canPlace(i,j):
				yield (i,j)

#returns a tuple(pos, score) indicating the best move that can possibly be made by curPlayer.
#recurses `plies` times if a value for `plies` is supplied; recurses indefinitely otherwise. (not recommended for anything more complicated than tic-tac-toe)
@memoize
def getBestMove(state, curPlayer, otherPlayer, plies=None):
	if plies == 0 or state.isGameOver():
		return (None, value(state, curPlayer, otherPlayer))
	bestMove = None
	bestScore = -9999
	for move in possibleMoves(state):
		nextState = state.copy()
		nextState.place(*move)
		_, score = getBestMove(nextState, otherPlayer, curPlayer, (None if plies == None else plies-1))
		if -score > bestScore:
			bestScore = -score
			bestMove = move
	return bestMove, bestScore