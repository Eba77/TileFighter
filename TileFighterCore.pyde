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
from Polytopes import *
from Objects import *
from PlayerFile import *

current_tile = None
player = None

def setup():
    global current_tile, player
    fullScreen(P2D)
    frameRate(DESIRED_FRAME_RATE)
    first_biome_v = BiomeVertex(MetaBiome(VertexConfiguration([[3] * 6, [3, 4, 3, 4, 3]]), first_biome=TEST_4_6_12), [0, 0], 0, (0, 0), 1)
    first_biome_v.generate(depth=1)
    first_biome = first_biome_v.getFriends()[0]
    first_biome.generateEdges()
    current_biome = BiomeVertex.getPolytopeOn(BIOME_POLYTOPE, [0, 0]).getAsBiome()
    first_vertex = TileVertex(current_biome(), [0, 0], 0, (0, 0), 1)
    first_vertex.generate(depth=1)
    current_tile = first_vertex.getFriends()[0]
    current_tile.generateEdges()
    player = Player(current_tile._position)
    print "Vertices on initial gen: ", len(Polytope.all_polytopes[TILE_POLYTOPE, TileVertex])
    print "Tiles on initial gen: ", len(Polytope.all_polytopes[TILE_POLYTOPE, TileFace])

def posOnScreen(pos, leniency):
    """
    Returns true if the point is on the screen
    Leniency specifies how far away it can be
    """
    distance = [
        abs(pos[0] - player.getPosition()[0]) - leniency,
        abs(pos[1] - player.getPosition()[1]) - leniency
    ]
    return distance[0] < width / 2 and distance[1] < height / 2

ticks = 0
def draw():
    global ticks
    ticks += 1
    if ticks % DESIRED_FRAME_RATE == DESIRED_FRAME_RATE - 1:
        # Print the frame rate - docs say its only accurate
        # after a few milliseconds, so we make it wait till
        # the end of the first second to report it
        print "Frame Rate: ", frameRate
    
    # First, we do a continuous update on all things:
    for obj in TileBound.all_objects:
        obj.continuousUpdate()
        
    pushMatrix()
    translate(width / 2 - player.getPosition()[0], height / 2 - player.getPosition()[1])
    background(150)
    partialGens = set({})
    for tile in Polytope.all_polytopes[TILE_POLYTOPE, TileFace]:
        if posOnScreen(tile.getPosition(), 300):
            if DRAW_FACES:
                tile.drawTile()
            if tile.notCompletelyGenerated() or tile.missingEdges():
                partialGens.add(tile)
    for tile in partialGens:
        # Any tile that is onscreen needs to be fully generated!
        tile.fullyGenerate()
        tile.drawTile()
        
    # Update the biome generation
    partialBiomes = set({})
    for biome in Polytope.all_polytopes[BIOME_POLYTOPE, BiomeFace]:
        if posOnScreen(biome.getPosition(), 300):
            if biome.notCompletelyGenerated() or biome.missingEdges():
                partialBiomes.add(biome)
    for biome in partialBiomes:
        # Any biome that is onscreen needs to be fully generated!
        biome.fullyGenerate()
        
    # Highlight tile that the cursor is on
    tile_pointing_at = TileFace.getPolytopeOn(TILE_POLYTOPE, getMouse())
    if tile_pointing_at is not None:
        if DRAW_FACES:
            tile_pointing_at.highlight()
        
    if DRAW_EDGES:
        for edge in Polytope.all_polytopes[TILE_POLYTOPE, TileEdge]:
            if posOnScreen(edge.getPosition(), 40):
                edge.drawEdge()
        
    if DRAW_VERTICES:
        for vert in Polytope.all_polytopes[TILE_POLYTOPE, TileVertex]:
            if posOnScreen(vert.getPosition(), 40):
                vert.drawVertex()
        
    # Draw all objects
    for obj in TileBound.all_objects:
        obj.drawObject()
        
    popMatrix()
    
    # Draw UI stuffs, these are done in screen coordinates!
    stroke(0)
    fill(0)
    text("TileFighter Version " + VERSION, 50, 50, 64)
    # Note that biomes exist using dual tilings
    temp = BiomeVertex.getPolytopeOn(BIOME_POLYTOPE, getMouse())
    text("Biome: " + str(temp.getAsBiome() if temp is not None else temp), 50, 70, 64)
        
    # Garbage collection; delete finished animations
    TileBound.all_objects = {obj for obj in TileBound.all_objects if not (isinstance(obj, Animation) and not obj._is_moving)}
        
def getMouse():
    return [mouseX - width / 2 + player.getPosition()[0], mouseY - height / 2 + player.getPosition()[1]]
    
def mousePressed():
    """
    Move player
    TODO: If tile not empty, attack denizen with stab attack!
    """
    player.move(TileFace.getPolytopeOn(TILE_POLYTOPE, getMouse()))
    
def keyPressed():
    """
    While this doesn't formally take a parameter, under-the-hood it uses a magic global variable
    called `key` which stores the most recent key pressed!
    """
    if key == ESC:
        print "Vertices explored: ", len(Polytope.all_polytopes[TILE_POLYTOPE, TileVertex])
        print "Tiles explored: ", len(Polytope.all_polytopes[TILE_POLYTOPE, TileFace])
        exit()
    if key == 'z' or key == 'Z':
        player.swipe()
