#Two objects have a dispatcher-listener relationship when the dispatcher sends an alert to its listeners when its internal state changes.
#The Dispatcher class is an abstract base class for any object that wishes to be a dispatcher.

class Dispatcher:
	def __init__(self):
		self.listeners = []

	def registerListener(self, listener):
		self.listeners.append(listener)

	#sends an alert to all listeners.
	def alert(self, fnName, *args):
		for listener in self.listeners:
			if hasattr(listener, fnName):
				getattr(listener, fnName)(self, *args)