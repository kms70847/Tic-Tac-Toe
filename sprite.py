#Sprite stuff

import time
import math

class Point:
	def __init__(self, *args):
		if len(args) == 2:
			self.x, self.y = args
		else:
			p = args[0]
			if isinstance(p, Point):
				self.x, self.y = p.x, p.y
			else:
				self.x, self.y = p[0], p[1]
	def __add__(self, other):
		return Point(self.x + other.x, self.y + other.y)
	def __repr__(self):
		return "({}, {})".format(int(self.x), int(self.y))

def distance(a,b):
	dx = b.x - a.x
	dy = b.y - a.y
	return math.sqrt(dx**2 + dy**2)

def midpoint(a, b, amt=0.5):
	x = b.x*amt + a.x*(1-amt)
	y = b.y*amt + a.y*(1-amt)
	return Point(x,y)

class BoundingBox:
	def __init__(self, *points):
		if len(points) == 0: raise ArgumentException, "need at least one point for initializer"
		p = points[0]
		self.left = p.x
		self.right = p.x
		self.top = p.y
		self.bottom = p.y
		for p in points[1:]:
			self.add(p)
	def add(self, obj):
		if isinstance(obj, Point):
			p = obj
			if p.x < self.left: self.left = p.x
			if p.x > self.right: self.right = p.x
			if p.y < self.top: self.top = p.y
			if p.y > self.bottom: self.bottom = p.y
			return
		if isinstance(obj, BoundingBox):
			p0 = Point(obj.left, obj.top)
			p1 = Point(obj.right, obj.bottom)
			self.add(p0)
			self.add(p1)
	def getTopLeft(self):
		return Point(self.left, self.top)

class Sprite:
	def __init__(self):
		pass

class LineSprite(Sprite):
	def __init__(self, x0, y0, x1, y1):
		self.p0 = Point(x0, y0)
		self.p1 = Point(x1, y1)
		self.item = None
	def getBoundingBox(self):
		return BoundingBox(self.p0, self.p1)
	def draw(self, canvas):
		self.canvas = canvas
		if not self.item:
			self.item = self.canvas.create_line(self.p0.x, self.p0.y, self.p1.x, self.p1.y)
		else:
			self.canvas.coords(self.item, self.p0.x, self.p0.y, self.p1.x, self.p1.y)
	#relative move
	def move(self, dx, dy):
		ds = Point(dx,dy)
		self.p0 += ds
		self.p1 += ds
		if self.item and self.canvas:
			self.canvas.move(self.item, dx, dy)
	#absolute move
	def move_to(self, x, y):
		bb = self.getBoundingBox()
		dx = x - bb.left
		dy = y - bb.top
		self.move(dx, dy)
	def __repr__(self):
		return "<{}, {}>".format(self.p0, self.p1)

class CircleSprite(Sprite):
	def __init__(self, x0, y0, radius):
		self.p = Point(x0, y0)
		self.radius = radius
		self.item = None
	def getBoundingBox(self):
		return BoundingBox(self.p, self.p + Point(2*self.radius, 2*self.radius))
	def draw(self, canvas):
		self.canvas = canvas
		bb = self.getBoundingBox()
		if not self.item:
			self.item = self.canvas.create_oval(bb.left, bb.top, bb.right, bb.bottom)
		else:
			self.canvas.coords(self.item, bb.left, bb.top, bb.right, bb.bottom)
	#relative move
	def move(self, dx, dy):
		ds = Point(dx,dy)
		self.p += ds
		if self.item and self.canvas:
			self.canvas.move(self.item, dx, dy)
	#absolute move
	def move_to(self, x, y):
		bb = self.getBoundingBox()
		dx = x - bb.left
		dy = y - bb.top
		self.move(dx, dy)
	#todo: actually implement
	def __repr__(self):
		return "<{}, {}>".format(self.p, self.radius)

class PolySprite(Sprite):
	def __init__(self, points, **options):
		self.points = points
		self.item = None
		self.options = options
		options["width"] = options.get("width", 1)
		options["fill"] = options.get("fill", "")
		options["outline"] = options.get("outline", "black")
	def getBoundingBox(self):
		return BoundingBox(*self.points)
	def draw(self, canvas):
		self.canvas = canvas
		coords = []
		for p in self.points:
			coords.append(p.x)
			coords.append(p.y)
		if not self.item:
			self.item = self.canvas.create_polygon(*coords, **self.options)
		else:
			self.canvas.coords(self.item, *coords)
	def move(self, dx, dy):
		ds = Point(dx, dy)
		self.points = [p + ds for p in self.points]
		if self.item and self.canvas:
			self.canvas.move(self.item, dx, dy)
	def move_to(self, x, y):
		bb = self.getBoundingBox()
		dx = x - bb.left
		dy = y - bb.top
		self.move(dx, dy)
	def __repr__(self):
		return "<{}>".format(self.points)

#Event stuff
class Event:
	def __init__(self):
		pass
	def And(self, event):
		return SimultaneousEvent(self, event)
	def Then(self, event):
		return ConcurrentEvent(self, event)

class SimultaneousEvent(Event):
	def __init__(self, *events):
		self.events = list(events)
	def tick(self, curTime):
		for event in self.events:
			event.tick(curTime)
		self.events = filter(lambda e: not e.done(), self.events)
	def add(self, event):
		self.events.append(event)
	def done(self):
		return len(self.events) == 0

class ConcurrentEvent(Event):
	def __init__(self, *events):
		self.events = list(events)
	def tick(self, curTime):
		if self.done(): return
		self.events[0].tick(curTime)
		if self.events[0].done():
			self.events = self.events[1:]
	def add(self, event):
		self.events.append(event)
	def done(self):
		return len(self.events) == 0

#attaches a sprite to a canvas
class CreateEvent(Event):
	def __init__(self, sprite, canvas):
		self.sprite = sprite
		self.canvas = canvas
		self.isDone = False
	def tick(self, curTime):
		self.sprite.draw(self.canvas)
		self.isDone = True
	def done(self):
		return self.isDone

#abstract class for any event that takes a fixed amount of time
class TimedEvent(Event):
	def __init__(self, totalTime):
		self.started = False
		self.isDone = False
		self.totalTime = totalTime
	def start(self):
		self.started = True
		self.startTime = time.time()
		self.amountDone = 0
	def tick(self, curTime):
		if not self.started:
			self.start()

		self.timeElapsed = curTime - self.startTime

		try:
			self.amountDone = self.timeElapsed / float(self.totalTime)
		except ZeroDivisionError:
			self.amountDone = 1

		if self.amountDone >= 1:
			self.isDone = True
	def done(self):
		return self.isDone

class TweenEvent(TimedEvent):
	def __init__(self, sprite, x, y, totalTime):
		TimedEvent.__init__(self, totalTime)
		self.sprite = sprite
		self.destination = Point(x,y)
		
	def start(self):
		TimedEvent.start(self)
		self.origin = self.sprite.getBoundingBox().getTopLeft()
	def tick(self, curTime):
		TimedEvent.tick(self, curTime)

		if self.isDone:
			self.sprite.move_to(self.destination.x, self.destination.y)
		else:
			p = midpoint(self.origin, self.destination, self.amountDone)
			self.sprite.move_to(p.x, p.y)

#changes the color of a sprite over time
class ColorChangeEvent(TimedEvent):
	def __init__(self, sprite, initialColor, targetColor, totalTime):
		TimedEvent.__init__(self, totalTime)
		self.sprite = sprite
		self.initialColor = initialColor
		self.targetColor = targetColor
	def setColor(self, color):
		def colorFromTuple(color):
			def toHex(x):
				ret = hex(x)[2:]
				while len(ret) < 2: ret = "0" + ret
				return ret
			
			colorStr = "#{}{}{}".format(toHex(color[0]), toHex(color[1]), toHex(color[2]))
			if len(colorStr) != 7:
				raise Exception, "color tuple {} converted to badly formatted string {}".format(color, colorStr)
			return colorStr
		item = self.sprite.item
		color = colorFromTuple(color)
		self.sprite.canvas.itemconfigure(item, fill=color)
	def midColor(self, a,b,m):
		midFunc = lambda a,b: a*(1-m) + b*(m)
		r = int(midFunc(a[0], b[0]))
		g = int(midFunc(a[1], b[1]))
		b = int(midFunc(a[2], b[2]))
		return (r,g,b)
	def tick(self, curTime):
		TimedEvent.tick(self, curTime)
		
		if self.isDone:
			self.setColor(self.targetColor)
		else:
			c = self.midColor(self.initialColor, self.targetColor, self.amountDone)
			self.setColor(c)
	def done(self):
		return self.isDone

#draws a line over time
class DrawEvent(TimedEvent):
	def __init__(self, canvas, totalTime, x0, y0, x1, y1):
		TimedEvent.__init__(self, totalTime)
		self.canvas = canvas
		self.p0 = Point(x0, y0)
		self.p1 = Point(x1, y1)
	def start(self):
		TimedEvent.start(self)
		self.item = self.canvas.create_line(self.p0.x, self.p0.y, self.p0.x, self.p0.y)
	def tick(self, curTime):
		TimedEvent.tick(self, curTime)
		if self.isDone:
			p = self.p1
		else:
			p = midpoint(self.p0, self.p1, self.amountDone)
		self.canvas.coords(self.item, self.p0.x, self.p0.y, p.x, p.y)