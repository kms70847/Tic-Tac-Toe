# File: hello1.py

from Tkinter import *
from sprite import *

import time
import util

#object which allows Events to be applied to a canvas.
class Gui:
	def __init__(self, canvas):
		self.canvas = canvas
		self.events = SimultaneousEvent()
		self.idle()
	def add(self, obj):
		if isinstance(obj, Sprite):
			self.add(CreateEvent(obj, self.canvas))
			return
		if isinstance(obj, Event):
			self.events.add(obj)
	def addAfter(self, event):
		self.events = ConcurrentEvent(self.events, event)
	#removes all pending events and clears the canvas.
	def reset(self):
		self.canvas.delete(*self.canvas.find_all())
		self.events = SimultaneousEvent()
	def idle(self):
		self.canvas.after(1000/600, self.idle)
		self.events.tick(time.time())

#gets the width and height of the canvas.
def size(canvas):
	return (int(canvas.cget(p)) for p in "width height".split())

#misc events that CanvasView requires
def drawGridEvent(canvas, numVerticalLines, numHorizontalLines, totalTime = 1.0):
	width, height = size(canvas)
	ret = SimultaneousEvent()
	for i in range(numVerticalLines):
		x = (i+1) * width/(numVerticalLines+1)
		ret.add(DrawEvent(canvas, totalTime, x,0, x,height))
	for i in range(numHorizontalLines):
		y = (i+1) * height/(numHorizontalLines+1)
		ret.add(DrawEvent(canvas, totalTime, 0,y, width,y))
	return ret

import math
#makes an X shaped object at (0,0), whose bounding box's width and height are equal to `size`
def makeX(size):
	#rotates point a about point c by `angle` radians counterclockwise.
	def rotateAbout(a, c, angle):
		curAngle = math.atan2(a.y-c.y, a.x-c.x)
		magnitude = distance(a,c)
		curAngle += angle
		dx = math.cos(curAngle)*magnitude
		dy = math.sin(curAngle)*magnitude
		return Point(c.x+dx, c.y+dy)
		
	#r represents the fatness of the x's limbs. r=0 is thin, r=1 is fat.
	r = 0.3
	
	a = Point(r*size/2, 0)
	
	h = size * (1-r) / 2
	b = Point(a.x+h, a.y+h)
	
	c = Point(size - a.x, 0)
	
	center = Point(size/2,size/2)
	d,e,f = [rotateAbout(p, center, 2*math.pi/4.0) for p in (a,b,c)]
	g,h,i = [rotateAbout(p, center, 2*math.pi/4.0) for p in (d,e,f)]
	j,k,l = [rotateAbout(p, center, 2*math.pi/4.0) for p in (g,h,i)]
	points = [a,b,c,d,e,f,g,h,i,j,k,l]
	return PolySprite(points)

#hmm, maybe I should just make a RectSprite class?
def makeRect(tl, br):
	points = []
	points.append(Point(tl.x, tl.y))
	points.append(Point(br.x, tl.y))
	points.append(Point(br.x, br.y))
	points.append(Point(tl.x, br.y))
	return PolySprite(points, outline="")

class CanvasView:
	def __init__(self, state, canvas):
		self.canvas = canvas
		self.gui = Gui(canvas)
		
		self.setState(state, True)
		
		#per-slot background panels. These can change color. Good for decoration.
		self.backgroundPanels = util.make2dArray(state.width, state.height, None)
		for x in range(state.width):
			for y in range(state.height):
				sprite = makeRect(Point(*self.getCornerPos(x,y)), Point(*self.getCornerPos(x+1, y+1)))
				self.gui.add(sprite)
				self.backgroundPanels[x][y] = sprite
		
	def setState(self, state, useFancyAnimations=True):
		#if we ever implement State::unregisterListener, unregister from the previous state if one exists
		self.state = state
		
		self.state.registerListener(self)
		
		self.gui.reset()
		
		#grid drawing is instantaneous if we don't use fancy animations
		animationTime = 0.0
		if useFancyAnimations:
			animationTime = 1.0
		self.gui.add(drawGridEvent(self.canvas, self.state.width-1, self.state.height-1, animationTime))
		
		self.sprites = util.make2dArray(self.state.width,self.state.height, None)
		for x in range(self.state.width):
			for y in range(self.state.height):
				if state.get(x,y) != None:
					sprite = self.makePiece(state.get(x,y), x, y)
					self.sprites[x][y] = sprite
					self.gui.add(sprite)

	#returns the width and height, in pixels, of any slot in the gui.
	def slotSize(self):
		width, height = size(self.canvas)
		return (width / self.state.width, height/ self.state.height)
	#gets the pixel coordinates of the upper left hand corner of the grid slot at position (x,y)
	def getCornerPos(self, x, y):
		slotWidth, slotHeight = self.slotSize()
		return (x*slotWidth, y*slotHeight)
	#gets the pixel coordinates of the center of the grid slot at position (x,y)
	def getCenterPos(self, x,y):
		width, height = size(self.canvas)
		slotWidth = width / self.state.width
		slotHeight = height / self.state.height
		x, y = self.getCornerPos(x,y)
		return (x+ slotWidth/2, y+slotHeight/2)
	#suppose you want to position a sprite so it is centered in the (x,y) slot.
	#this function returns the coordinates of that sprite's top left corner.
	def getPiecePos(self, sprite, x, y):
		centerX, centerY = self.getCenterPos(x,y)
		spriteSize = (lambda bb: bb.right - bb.left)(sprite.getBoundingBox())
		x = centerX - spriteSize / 2
		y = centerY - spriteSize / 2
		return (x,y)

	def makePiece(self, player, x, y, spriteSize = None):
		if spriteSize == None:
			spriteSize = min(self.slotSize()) * 0.75

		if player == 1:
			sprite = makeX(spriteSize)
		else:
			sprite = CircleSprite(0,0,spriteSize / 2)
		x,y = self.getPiecePos(sprite, x, y)
		sprite.move_to(x,y)
		return sprite
	
	#causes the background of the given slot to change color
	def throb(self, x, y):
		panel = self.backgroundPanels[x][y]
		defaultGray = (240,240,240)
		red = (255,128,128)
		self.gui.add(makeThrobEvent(panel, defaultGray, red, 0.1))
	def piecePlaced(self, state, player, x, y):
		#the sprite is created offscreen. decide where the sprite should come from.
		#these are mostly arbitrary.
		startPositions = {
			(0,0): (-1,-1),
			(1,0): (1,-1),
			(2,0): ( 3,-1),
			(2,1): ( 3, 1),
			(2,2): ( 3, 3),
			(1,2): ( 1, 3),
			(0,2): (-1, 3),
			(0,1): (-1, 1),
			(1,1): ( 1,-1)
		}
		startPos = startPositions.get((x,y), (-1,-1))
		sprite = self.makePiece(player, *startPos)
		self.sprites[x][y] = sprite

		self.gui.addAfter(CreateEvent(sprite, self.canvas))

		distanceTraveled = math.sqrt((x-startPos[0])**2 + (y-startPos[1])**2)
		travelSpeed = 0.125 #in slots/second 
		travelTime = distanceTraveled * travelSpeed

		destX, destY = self.getPiecePos(sprite, x, y)
		self.gui.addAfter(TweenEvent(sprite, destX, destY, travelTime))
	def gameWon(self, state, player):
		if player == None: return
		throbEvents = []
		for x in range(state.width):
			for y in range(state.height):
				if state.get(x,y) == player:
					ev = makeThrobEvent(self.sprites[x][y], (240,240,240), (128,255,128), 0.1)
					throbEvents.append(ev)
		self.gui.addAfter(SimultaneousEvent(*throbEvents))
	def tick(self, curTime):
		self.gui.tick(curTime)

def makeThrobEvent(sprite, startColor, midColor, totalTime):
	return ColorChangeEvent(sprite, startColor, midColor, totalTime/2).Then(ColorChangeEvent(sprite, midColor, startColor, totalTime/2))