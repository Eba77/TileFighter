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
from Objects import *

current_tile = None
player = None

def setup():
    global current_tile, player
    fullScreen()
    frameRate(60)
    first_vertex = Vertex(HEX_FOREST(), [0, 0], 0, (0, 0), 1)
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
    text("TileFighter Version " + VERSION, 50, 50, 64)
        
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
