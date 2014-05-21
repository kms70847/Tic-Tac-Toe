from state import State

def serialize(state):
	ret = ""
	for i in range(state.width):
		for j in range(state.height):
			ret = ret + {1:'x',2:'o',None:' '}[state.data[i][j]]
	return ret

def deserialize(msg):
	state = State()
	for idx in range(state.width * state.height):
		i = idx / state.height
		j = idx % state.height
		state.data[i][j] = {'x':1,'o':2,' ':None}[msg[idx]]
	numX = len(list(i for i in msg if i == 'x'))
	numO = len(list(i for i in msg if i == 'o'))
	if numX > numO:
		state.curPlayer = 2
	else:
		state.curPlayer = 1
	return state