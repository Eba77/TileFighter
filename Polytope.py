"""
`Polytope.py`

Handles generation of Vertices and Tiles (faces) at a more micro
level than the `Biomes.py` file, which is more concerned with
big-picture stuff.
"""

from Biomes import *
from Geometry import *
from HelperTools import *
from MagicNumbers import *
import math

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
        
    def getPosition(self):
        return self._position
    
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
        self._attributes = self._biome.getTileAttributes(self.getSides())
        Tile.all_tiles.add(self)
        
    def getMonotonicVertices(self):
        """
        Returns a list of vertices, sorted in terms of their angle away from center
        This will only work for CONVEX polygons!
        (Well, okay, it will work for nonconvex too, it just won't be useful; two
        adjacent vertices in the list won't necessarily be connected if nonconvex)
        """
        to_return = list(self._vertices)
        to_return.sort(
            key=lambda vert: atan2(
                vert.getPosition()[1] - self._position[1],
                vert.getPosition()[0] - self._position[0]
            )
        )
        return to_return
        
        
    def damage(self, how_much):
        if self._attributes.isDestructible():
            self._attributes = self._attributes.destroy()
        
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
    
    def getAttributes(self):
        return self._attributes
  
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
            self._attributes.getColor(),
            self._attributes.getStroke()
        )
        """irregularPolygon(
            [0, 0],
            [[x.getPosition()[0] - self._position[0], x.getPosition()[1] - self._position[1]] for x in self.getMonotonicVertices()],
            self._attributes.getColor(),
            self._attributes.getStroke()
        )"""
        if highlight is not None:
            regularPolygon(
                [0, 0],
                self._radius * 0.5,
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
        if self.getAttributes().isPassable():
            self.drawTile(0, color(255, 255, 0, 100))
        else:
            self.drawTile(0, color(255, 0, 0, 100))
            
    def isAdjacent(self, adj):
        return adj in self._adjacents
