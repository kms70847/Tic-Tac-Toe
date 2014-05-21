#decorator for object methods.
#when a deferred method is called, the method body doesn't execute right away.
#instead, it's added to the deferredCalls[] array, which can then be executed by calling checkDeferredCalls.
def deferred(fn):
    def deferredFn(*args):
        obj = args[0]
        obj.deferredCalls.append(lambda: fn(*args))
    return deferredFn

class Deferrer:
    def __init__(self):
        self.deferredCalls = []
    def checkDeferredCalls(self):
        while len(self.deferredCalls) > 0:
            fn = self.deferredCalls[0]
            self.deferredCalls = self.deferredCalls[1:]
            fn()
