import itertools
import math
from Biomes import *

DRAW_VERTICES = True
CLOSENESS_CONSTANT = 1 # how close two tiles have to be to be considered the same

# Note that Python Processing is built on Jython
# and thus we can't use certain libraries, like
# crucially *numpy*!
# So we have to reinvent the wheel a bit
def frange(start, stop, step):
    """
    Like range, but works with floats
    Would have used numpy.linspace
    but that wasn't an option as there
    ain't any numpies in this here code.
    """
    for i in itertools.count():
        to_return = start + step * i
        if to_return < stop:
            yield to_return
        else:
            break
        
def square_dist(pos_1, pos_2):
    return sum([(x-y)**2 for x, y in zip(pos_1, pos_2)])

# Taken from processing tutorial, modified slightly
# https://processing.org/examples/regularpolygon.html
# why re-invent the wheel?
cached_polies = dict({})
def regularPolygon(pos, radius, npoints, draw_angle, in_fill = None, in_stroke = None):
    """
    Draws a regular polygon of radius `radius`, with `npoints` sides,
    at position `pos`, with fill/stroke in `in_fill`/`in_stroke`
    """
    if npoints % 2 == 1:
        # This algorithm would point apothem where we want
        # radius to point, so we swap them by rotating the
        # distance between radius and apothem
        draw_angle += PI / npoints
    pushMatrix()
    translate(pos[0], pos[1])
    rotate(draw_angle)
    scale(radius)
    if npoints not in cached_polies:
        poly = createShape()
        poly.beginShape()
        angle = TWO_PI / npoints
        for a in frange(0, TWO_PI, angle):
            sx = cos(a)
            sy = sin(a)
            poly.vertex(sx, sy)
        poly.endShape(CLOSE)
        cached_polies[npoints] = poly
    if in_fill is not None:
        cached_polies[npoints].setFill(in_fill)
    if in_stroke is not None:
        cached_polies[npoints].setStroke(in_stroke)
    cached_polies[npoints].setStrokeWeight(1.0/radius)
    shape(cached_polies[npoints])
    popMatrix()
    
"""
^^^ Really cool effect with `regularPolygon`
Play in TEST_3_3_3_3_3_3_and_3_4_3_4_3, but don't have the npoints%2==1 bit and rotate by
the negative draw angle.  Gives an interesting look!
"""

class Vertex:
    all_vertices = set({})
    
    @classmethod
    def getAllVerticesNear(cls, pos, epsilon):
        return {v for v in cls.all_vertices if square_dist(pos, v._position) < epsilon**2}
    
    @classmethod
    def getNearestVertexWithin(cls, pos, epsilon):
        """
        Returns None if no vertex within epsilon
        """
        if len(cls.all_vertices) == 0:
            return None
        to_return = min(cls.all_vertices, key=lambda v: square_dist(pos, v._position))
        if square_dist(pos, to_return._position) < epsilon**2:
            return to_return
        return None
    
    def __init__(self, b, p, h, def_tup, s):
        """
        Heading is the starting angle it uses when placing vertices
        Index offset is the starting part of the Vertex Config that it uses
        Spin should be 1 or -1 and indicates direction around itself to travel
        when placing tiles
        `def_tup` is the (vertex type, edge numeral) pair
        """
        self._biome = b
        self._position = p
        self._heading = math.fmod(h, TWO_PI)
        self._vertex_type = def_tup[0]
        self._index_offset = def_tup[1]
        self._tiles = [None for x in range(self._biome.getTileNumAtVertex(self._vertex_type))]
        self._spin = 1 if s > 0 else -1
        
        # List of vertices connected to this by an edge
        # Position 0 is vertex between -1th and 0th adjacent tile
        self._friend_vertices = [None for x in range(self._biome.getTileNumAtVertex(self._vertex_type))]
        
        Vertex.all_vertices.add(self)
        
    def isPartiallyGenerated(self):
        """
        If this vertex doesn't have all friends generated
        """
        return (
            len([vert for vert in self._friend_vertices if vert is None]) > 0
            or len([tile for tile in self._tiles if tile is None]) > 0
        )
        
    def generateTiles(self, depth):
        angle = self._heading
        for raw_idx, val in enumerate(self._tiles):
            # `raw_idx` indicates array position,
            # `idx` is position in vertex configuration
            idx = (raw_idx  + self._index_offset) % len(self._tiles)
            # Turning angle increment, split up into two parts
            # because it is affected by both current tile, and previous tile!
            # (technically this is the 'second' part, since loop is cyclical)
            prev_angle = angle # used for friend vertex calculation
            angle += self._spin * self._biome.getVertexAngle(self._vertex_type, idx) / 2
            radius = self._biome.getRadius(self._vertex_type, idx)
            side_length = self._biome.getSideLength(self._vertex_type, idx)
            if val is None:
                new_pos = [
                    cos(angle) * radius + self._position[0],
                    sin(angle) * radius + self._position[1]
                ]
                tile = Tile.getNearestTileWithin(new_pos, CLOSENESS_CONSTANT)
                if tile is None:
                    tile = Tile(
                        self._biome,
                        new_pos,
                        radius,
                        (self._vertex_type, idx),
                        angle,
                        {self}
                    )
                else:
                    tile.addVertex(self)
                self._tiles[raw_idx] = tile
            else:
                val.addVertex(self)
            if raw_idx > 0:
                # Make tiles adjacent to eachother correctly
                # note that addAdjacent works two-ways, but is a set
                # so no worries about duplicates.
                self._tiles[raw_idx].addAdjacent(self._tiles[raw_idx-1])
                
                # Add vertices at tile intersections
                new_pos = [
                    cos(prev_angle) * side_length + self._position[0],
                    sin(prev_angle) * side_length + self._position[1]
                ]
                vert = Vertex.getNearestVertexWithin(new_pos, CLOSENESS_CONSTANT)
                if vert is None:
                    """
                    Calculating the heading requires drawing out a diagram to figure out,
                    if you're curious where it came from (fairly simple to show geometrically,
                    but it's hard to explain englishically)
                    """
                    new_heading = PI + prev_angle
                    vert = Vertex(self._biome, new_pos, new_heading, self._biome.swap(self._vertex_type, idx), -self._spin)
                self._friend_vertices[raw_idx] = vert
                self._tiles[raw_idx].addVertex(vert)
                
            # Second (technically 'first') part of turning angle increment
            angle += self._spin * self._biome.getVertexAngle(self._vertex_type, idx) / 2
           
        # Match up beginning with end
        self._tiles[0].addAdjacent(self._tiles[-1])
        new_pos = [
            cos(angle) * side_length + self._position[0],
            sin(angle) * side_length + self._position[1]
        ]
        vert = Vertex.getNearestVertexWithin(new_pos, CLOSENESS_CONSTANT)
        if vert is None:
            new_heading = PI + angle
            vert = Vertex(self._biome, new_pos, new_heading, self._biome.swap(self._vertex_type, self._index_offset), -self._spin)
        self._friend_vertices[0] = vert
        self._tiles[0].addVertex(vert)
        
        # Recursive generation!
        if depth > 1:
            for vert in self._friend_vertices:
                vert.generateTiles(depth-1)
        
    def drawVertex(self):
        """
        Really should only be used for debugging!
        """
        pushMatrix()
        translate(self._position[0], self._position[1])
        stroke(0)
        fill(255)#self._heading / TWO_PI * 255)
        circle(0, 0, 20)
        fill(0, 0, 200)
        text(str([self._vertex_type, self._index_offset]), -6, 6, 16)
        
        # Draw line pointing in direction of `heading`
        stroke(0, 255, 0)
        line(0, 0, 30 * cos(self._heading), 30 * sin(self._heading))
        popMatrix()
                    
                
    def __getitem__(self, n):
        return self._tiles[n]

class Tile:
    all_tiles = set({})
    
    @classmethod
    def getAllTilesNear(cls, pos, epsilon):
        return {v for v in cls.all_tiles if square_dist(pos, v._position) < epsilon**2}
    
    @classmethod
    def getNearestTileWithin(cls, pos, epsilon):
        """
        Returns None if no tile within epsilon
        """
        if len(cls.all_tiles) == 0:
            return None
        to_return = min(cls.all_tiles, key=lambda t: square_dist(pos, t._position))
        if square_dist(pos, to_return._position) < epsilon**2:
            return to_return
        return None
    
    @classmethod
    def getTileOn(cls, pos):
        """
        Gets the tile that the position pos is on
        Note that distances from a tile are weighted by radius
        This won't be possible for irregular tilings :/
        Returns None if not on a tile
        """
        if len(cls.all_tiles) == 0:
            return None
        return min(cls.all_tiles, key=lambda t: sqrt(square_dist(pos, t._position))/t.getApothem())
    
    def __init__(self, b, p, r, p_in_v, d_ang, verts):
        self._biome = b
        self._position = p
        self._radius = r
        self._color = self._biome.getTileColor(p_in_v)
        self._position_in_vertex = p_in_v
        self._adjacents = set({})
        self._vertices = verts
        self._draw_angle = d_ang
        Tile.all_tiles.add(self)
        
    def getAdjacents(self):
        return self._adjacents
    
    def isPartiallyGenerated(self):
        """
        If this tile doesn't have all adjacencies filled!
        """
        return len([x for x in self._vertices if x.isPartiallyGenerated()]) > 0
    
    def fullyGenerate(self):
        """
        Generate all adjacent vertices!
        """
        loop_count = 0
        while self.isPartiallyGenerated():
            assert loop_count < 100, "Something went wrong - stuck in an infinite generation loop!" + str(self.getSides()) + ";" + str(len(self._vertices)) + ";" + str(len(self._adjacents))
            loop_count += 1
            for vert in self._vertices:
                if vert.isPartiallyGenerated():
                    vert.generateTiles(depth=2)

        
    def addAdjacent(self, adj):
        if adj is not None:
            self._adjacents.add(adj)
            adj._adjacents.add(self)
            
    def addVertex(self, vert):
        """
        Unlike `addAdjacent`, this is not a reciprocal function;
        adding a vertex to a tile doesn't add tile to vertex
        """
        #print "AHHHH", vert, vert in self._vertices
        if vert is not None:
            self._vertices.add(vert)
  
    def getPosition(self):
        return self._position
    
    def getSides(self):
        return self._biome.getSides(*(self._position_in_vertex))
  
    def drawTile(self, depth, highlight = None):
        """
        Draws this tile, and all times within `depth`
        Note that this method is inefficient and will result
        in drawing tiles twice (if depth is two, it will draw this tile,
        draw adjacent tiles, and draw those tiles' adjacents -
        however this tile is adjacent to its adjacents, so it'll be drawn
        twice!)  Could be improved later
        """
        pushMatrix()
        translate(self._position[0], self._position[1])
        stroke(0)
        regularPolygon(
            [0, 0],
            self._radius,
            self.getSides(),
            self._draw_angle,
            self._color
        )
        if highlight is not None:
            regularPolygon(
                [0, 0],
                self._radius,
                self.getSides(),
                self._draw_angle,
                highlight
            )
        popMatrix()
        if DRAW_VERTICES:
            for vert in self._vertices:
                vert.drawVertex()
        if depth > 1:
            for adj in self._adjacents:
                if adj is not None:
                    adj.drawTile(depth - 1)
        
    def getTurningAngle(self):
        return self._biome.getTurningAngle(*self._position_in_vertex)
    
    def getApothem(self):
        """
        Similar to radius, heads to center of side rather than vertex
        """
        return self.getRadius() * cos(self.getTurningAngle() / 2)
    
    def getRadius(self):
        return self._radius
    
    def highlight(self):
        self.drawTile(0, color(255, 255, 0, 100))
        
    def isAdjacent(self, adj):
        return adj in self._adjacents
        
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
