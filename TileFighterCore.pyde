"""
`TileFighterCore.py`
This is the entry point to the application, and will likely be a bit of a mess!
Prototyping is often done in this file before things get factored out to their
own areas.

In theory this should just house the `setup`, `draw`, and event functions like
`keyPressed`, as well as any helper functions made specifically for those
methods.  In practice, this file could contain anything!
"""

import itertools
import math
from Biomes import *
from HelperTools import *
from Polytope import *
        
class TileBound:
    all_objects = set({})
    
    def __init__(self, pos, move_time = 10):
        """
        `self._move_time` is just the amount
        of ticks before done moving
        `self._move_steps` is a generator giving intermediate
        move points.
        """
        self._position = pos
        self._is_moving = False
        self._move_destination = None
        self._move_time = move_time
        self._move_steps = None
        
        TileBound.all_objects.add(self)
        
    def getTileOn(self):
        return Tile.getTileOn(self._position)
        
    def drawObject(self):
        print "No draw method!"
        
    def getPosition(self):
        return self._position
    
    def move(self, destination):
        if self._is_moving:
            # Can't move if already moving!
            return
        self._is_moving = True
        self._move_destination = destination.getPosition()
        initial_position = self.getPosition()
        difference = [
            self._move_destination[0] - initial_position[0],
            self._move_destination[1] - initial_position[1]
        ]
        def direc_r(r):
            return [initial_position[0] + difference[0] * r , initial_position[1] + difference[1] * r]
        self._move_steps = (direc_r(1.0 * i / self._move_time) for i in range(self._move_time))
            
        
    def continuousUpdate(self):
        """
        Used for animation stuff, TileBounds should not
        have logic based on this
        """
        if not self._is_moving:
            return
        try:
            self._position = next(self._move_steps)
        except StopIteration:
            self._position = self._move_destination
            self._is_moving = False
        
class Animation():
    """
    Class which gets destroyed when it is no longer moving
    """
    pass
        
class SwipeAttack(TileBound, Animation):
    def __init__(self, pos, weilder, radius):
        TileBound.__init__(self, pos)
        self._weilder = weilder
        self._is_moving = True
        self._center = pos
        self._radius = radius
        self._edge = [pos[0] + radius, pos[1]]
        self._old_edge = self._edge
        self._rot = 0
        self._old_rot = 0
        def direc_r(r):
            return [self._center[0] + self._radius * cos(r), self._center[1] + self._radius * sin(r)]
        self._move_steps = ((direc_r(i * TWO_PI / self._move_time), i * TWO_PI / self._move_time) for i in range(1, self._move_time + 1))
        
    def continuousUpdate(self):
        if not self._is_moving:
            return
        try:
            self._old_edge = self._edge
            self._old_rot = self._rot
            self._edge, self._rot = next(self._move_steps)
        except StopIteration:
            self._position = self._move_destination
            self._is_moving = False
            self._weilder._is_moving = False
            self._weilder._swipe_attack = None
            
    def drawObject(self):
        pushMatrix()
        translate(*(self._center))
        
        # First we draw the overall arc of the swipe
        stroke(0, 200, 255, 200)
        fill(0, 200, 255, 100)
        arc(0, 0, 2 * self._radius, 2 * self._radius, self._old_rot, self._rot)
        
        # Then we draw a thicker, smaller arc
        stroke(255, 255, 255, 255)
        fill(255, 255, 255, 200)
        arc(0, 0, 2 * self._radius, 2 * self._radius, self._old_rot + 0.7 * (self._rot - self._old_rot), self._rot)
        
        # And now the actual sword
        stroke(0, 255, 255, 255)
        line(0, 0, self._edge[0] - self._center[0], self._edge[1] - self._center[1])
        
        popMatrix()
    
class Player(TileBound):
    MAX_SWIPE_DIST = 250
    
    def __init__(self, pos):
        TileBound.__init__(self, pos)
        self._swipe_attack = None
        
    def move(self, destination):
        if not destination.isAdjacent(self.getTileOn()):
            # Can only move to adjacent tiles!
            return
        TileBound.move(self, destination)
        
    def swipe(self):
        """
        Triggers the player's arc attack
        """
        if self._is_moving:
            return
        # This is considered a 'move', so we have to set movement variables
        # to reasonable values.  `_move_steps` is set to forever give
        # the same position, so that no real moving happens.
        self._is_moving = True
        self._move_steps = (self._position for x in itertools.count())
        t_on = self.getTileOn()
        swipe_length = min(1.3 * (t_on.getApothem() + max((adj.getApothem() for adj in t_on._adjacents))), Player.MAX_SWIPE_DIST)
        self._swipe_attack = SwipeAttack(self._position, self, swipe_length)
        
    def drawObject(self):
        pushMatrix()
        
        # Draw actual player
        tile = self.getTileOn()
        tile_pos = tile.getPosition()
        translate(*(self.getPosition()))
        stroke(0)
        fill(0)
        circle(0, 0, 20)
        
        # Draw arrows hinting at possible moves
        stroke(255, 0, 0)
        if not self._is_moving:
            for t in tile.getAdjacents():
                t_pos = t.getPosition()
                difference = [
                    t_pos[0] - tile_pos[0],
                    t_pos[1] - tile_pos[1]
                ]
                magnitude = sqrt(difference[0]**2+difference[1]**2)
                direction = [
                    difference[0] / magnitude,
                    difference[1] / magnitude
                ]
                def direc_r(r):
                    return [direction[0] * r, direction[1] * r]
                line(*(direc_r(tile.getApothem()*0.8) + direc_r(tile.getApothem() + t.getApothem() * 0.2)))
        
        popMatrix()

current_tile = None
player = None

def setup():
    global current_tile, player
    fullScreen()
    frameRate(60)
    first_vertex = Vertex(TEST_3_3_3_3_6, [0, 0], 0, (0, 0), 1)
    first_vertex.generateTiles(depth=5)
    current_tile = first_vertex[0]
    player = Player(current_tile._position)
    print "Vertices on initial gen: ", len(Vertex.all_vertices)
    print "Tiles on initial gen: ", len(Tile.all_tiles)

def draw():
    # First, we do a continuous update on all things:
    for obj in TileBound.all_objects:
        obj.continuousUpdate()
        
    pushMatrix()
    translate(width / 2 - player.getPosition()[0], height / 2 - player.getPosition()[1])
    background(150)
    partialGens = set({})
    for tile in Tile.all_tiles:
        # Only want to draw tiles that are on the screen
        # subtracting out the radius for leinency
        distance = [
            abs(tile.getPosition()[0] - player.getPosition()[0]) - tile.getRadius(),
            abs(tile.getPosition()[1] - player.getPosition()[1]) - tile.getRadius()
        ]
        if distance[0] < width / 2 and distance[1] < height / 2:
            tile.drawTile(depth=1)
            if tile.isPartiallyGenerated():
                partialGens.add(tile)
    for tile in partialGens:
        # Any tile that is onscreen needs to be fully generated!
        tile.fullyGenerate()
        tile.drawTile(depth=1)
        
    # Highlight tile that the cursor is on
    tile_pointing_at = Tile.getTileOn(getMouse())
    if tile_pointing_at is not None:
        tile_pointing_at.highlight()
        
    # Draw all objects
    for obj in TileBound.all_objects:
        obj.drawObject()
        
    popMatrix()
    
    # Draw UI stuffs, these are done in screen coordinates!
    stroke(0)
    fill(0)
    text("TileFighter Version 0.1a [Alpha]", 50, 50, 64)
        
    # Garbage collection; delete finished animations
    TileBound.all_objects = {obj for obj in TileBound.all_objects if not (isinstance(obj, Animation) and not obj._is_moving)}
        
def getMouse():
    return [mouseX - width / 2 + player.getPosition()[0], mouseY - height / 2 + player.getPosition()[1]]
    
        
def mousePressed():
    """
    Move player
    TODO: If tile not empty, attack denizen with stab attack!
    """
    player.move(Tile.getTileOn(getMouse()))
    
        
# Since x button bar d/n exist in Python mode, this is an easy way to quit!
def keyPressed():
    """
    While this doesn't formally take a parameter, under-the-hood it uses a magic global variable
    called `key` which stores the most recent key pressed!
    """
    if key == ESC:
        print "Vertices explored: ", len(Vertex.all_vertices)
        print "Tiles explored: ", len(Tile.all_tiles)
        exit()
    if key == 'z' or key == 'Z':
        player.swipe()
