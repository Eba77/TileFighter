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

def definePolytope(poly):
    """
    Initializes a polytope, should be used as a decorator
    above the end-level polytope classes
    """
    Polytope.all_polytopes[poly] = set({})
    return poly

class Polytope:
    all_polytopes = dict({})
    
    @classmethod
    def getPolytopesNear(cls, pos, epsilon):
        """
        Note that this can be called as Vertex.getPolytopesNear(...),
        and that is the method to get all examples of a specific polytope!
        """
        return {p for p in Polytope.all_polytopes[cls] if square_dist(pos, p.getPosition()) < epsilon**2}
    
    @classmethod
    def getNearestPolytopeWithin(cls, pos, epsilon):
        """
        Returns None if no polytope within epsilon
        """
        if len(Polytope.all_polytopes[cls]) == 0:
            return None
        to_return = min(Polytope.all_polytopes[cls], key=lambda v: square_dist(pos, v.getPosition()))
        if square_dist(pos, to_return.getPosition()) < epsilon**2:
            return to_return
        return None
    
    @classmethod
    def getPolytopeOn(cls, pos):
        raise NotImplementedError
    
    def __init__(self, biome, position):
        self._biome = biome
        self._position = position
        self._attributes = self._biome.getTileAttributes(0) # Placeholder for now
        
    def getPosition(self):
        return self._position
    
    def getBiome(self):
        return self._biome
    
    def getAttributes(self):
        return self._attributes
    
    def damage(self, how_much):
        if self._attributes.isDestructible():
            self._attributes = self._attributes.destroy()
    
@definePolytope
class Edge(Polytope):
    """
    Edges are currently ignored in the generation process
    But in the future I'd like that to change!
    """
    pass
    
class Duals(Polytope):
    """
    This class captures the interrelated nature between Vertices and Faces!
    """
    
    @classmethod
    def getPolytopeOn(cls, pos):
        """
        Gets the polytope that the position pos is on
        Returns None if not on a tile
        """
        relevants = Polytope.all_polytopes[cls]
        if len(relevants) == 0:
            return None
        close_topes = sorted(relevants, key=lambda t: square_dist(pos, t.getPosition()))
        for tope in close_topes:
            if evenOddRule(tope.getPosition(), [dual_tope.getPosition() for dual_tope in tope.getMonotonic(tope._friends)]):
                return tope
        return None
    
    def getDual(self):
        if isinstance(self, Vertex):
            return Face
        elif isinstance(self, Face):
            return Vertex
        else:
            raise NotImplementedError
            
    def getSides(self):
        raise NotImplementedError
            
    def __init__(self, cls, biome, position, heading_, state):
        """
        `state` is the SigmaSwaps-relevant pair
        `spin` is clockwise/counterclockwise drawing indicator
        `_adjacents` are the polytopes of the same type as this that are connected
        `_friends` are the polytopes of the opposite type that are adjacent
            As an example, the vertices on a face are the friends of that face
        `_edges`  are the edges related to this polytope!
        """
        Polytope.__init__(self, biome, position)
        self._heading = math.fmod(heading_, TWO_PI)
        self._state = state
        self._adjacents = []
        self._friends = None # Implement these in child classes
        self._adjacents = None
        self._edges = None
        self._goal_friends = None # Amount of friends we need to reach
    
    def getMonotonic(self, to_be_monotonized):
        """
        Returns a list of vertices, sorted in terms of their angle away from center
        This will only work for CONVEX polygons!
        (Well, okay, it will work for nonconvex too, it just won't be useful; two
        adjacent vertices in the list won't necessarily be connected if nonconvex)
        
        Note, if we are a vertex, this will return a list of 'faces', but its best
        thought of as returning the vertices of this vertex-face in the dual tiling.
        """
        return sorted(
            list(to_be_monotonized),
            key=lambda friend: atan2(
                friend.getPosition()[1] - self._position[1],
                friend.getPosition()[0] - self._position[0]
            )
        )
        return to_return
        
    def getAdjacents(self):
        return self._adjacents
    
    def getFriends(self):
        return self._friends
    
    def isPartiallyGenerated(self):
        """
        Return true if not all friends have been generated
        """
        return len([x for x in self._friends if x is not None]) < self._goal_friends
            
    def isAdjacent(self, adj):
        return adj in self._adjacents
            
    def isFriend(self, friend):
        return friend in self._friends
    
    """
    These three are calculated directly from the geometry
    """
    def getTurningAngle(self):
        return 100
        raise NotImplementedError
        #return self._biome.getTurningAngle(*self._position_in_vertex)
    
    def getApothem(self):
        """
        Similar to radius, heads to center of edge rather than center of dual
        """
        return 100
        raise NotImplementedError
        #return self.getRadius() * cos(self.getTurningAngle() / 2)
    
    def getRadius(self):
        return 100
        raise NotImplementedError
        #return self._radius
        
    def getSides(self):
        if isinstance(self, Vertex):
            amount = self._biome.getTileNumAtVertex(self._state[0])
        elif isinstance(self, Face):
            amount = self._biome.getConfig()[self._state[0]][self._state[1]]
    
@definePolytope
class Vertex(Duals):
    """
    Vertices are the primary generator of our tilings.
    They are the dual of Faces.
    """
    
    def __init__(self, biome, position, heading_, state, spin):
        """
        `state` is the SigmaSwaps-relevant pair
        `spin` is clockwise/counterclockwise drawing indicator
        """
        Duals.__init__(self, Vertex, biome, position, heading_, state)
        self._spin = 1 if spin > 0 else -1
        self._goal_friends = self.getSides()
        self._friends = [None for x in range(self._goal_friends)]
        self._adjacents = [None for x in range(self._goal_friends)]
        
        Polytope.all_polytopes[Vertex].add(self)
        
    def getSides(self):
        return len(self._biome.getConfig()[self._state[0]])
        
    def generate(self, depth):
        angle = self._heading
        for raw_idx, val in enumerate(self._friends):
            # `raw_idx` indicates array position,
            # `idx` is position in vertex configuration
            idx = (raw_idx  + self._state[1]) % len(self._friends)
            # Turning angle increment, split up into two parts
            # because it is affected by both current tile, and previous tile!
            # (technically this is the 'second' part, since loop is cyclical)
            prev_angle = angle # used for friend vertex calculation
            angle += self._spin * self._biome.getVertexAngle(self._state[0], idx) / 2
            radius = self._biome.getRadius(self._state[0], idx)
            side_length = self._biome.getSideLength(self._state[0], idx)
            if val is None:
                new_pos = [
                    cos(angle) * radius + self._position[0],
                    sin(angle) * radius + self._position[1]
                ]
                tile = Face.getNearestPolytopeWithin(new_pos, CLOSENESS_CONSTANT)
                if tile is None:
                    tile = Face(
                        self._biome,
                        new_pos,
                        angle,
                        (self._state[0], idx),
                    )
                tile.addFriend(self)
                self._friends[raw_idx] = tile
            else:
                val.addFriend(self)
            if raw_idx > 0:
                # Make tiles adjacent to eachother correctly
                self._friends[raw_idx].addAdjacent(self._friends[raw_idx - 1])
                self._friends[raw_idx - 1].addAdjacent(self._friends[raw_idx])
                
                # Add vertices at tile intersections
                new_pos = [
                    cos(prev_angle) * side_length + self._position[0],
                    sin(prev_angle) * side_length + self._position[1]
                ]
                vert = Vertex.getNearestPolytopeWithin(new_pos, CLOSENESS_CONSTANT)
                if vert is None:
                    """
                    Calculating the heading requires drawing out a diagram to figure out,
                    if you're curious where it came from (fairly simple to show geometrically,
                    but it's hard to explain englishically)
                    """
                    new_heading = PI + prev_angle
                    vert = Vertex(self._biome, new_pos, new_heading, self._biome.swap(self._state[0], idx), -self._spin)
                self._adjacents[raw_idx] = vert
                self._friends[raw_idx].addFriend(vert)
                
            # Second (technically 'first') part of turning angle increment
            angle += self._spin * self._biome.getVertexAngle(self._state[0], idx) / 2
           
        # Match up beginning with end
        self._friends[0].addAdjacent(self._friends[-1])
        self._friends[-1].addAdjacent(self._friends[0])
        new_pos = [
            cos(angle) * side_length + self._position[0],
            sin(angle) * side_length + self._position[1]
        ]
        vert = Vertex.getNearestPolytopeWithin(new_pos, CLOSENESS_CONSTANT)
        if vert is None:
            new_heading = PI + angle
            vert = Vertex(self._biome, new_pos, new_heading, self._biome.swap(*self._state), -self._spin)
        self._adjacents[0] = vert
        self._friends[0].addFriend(vert)
        
        # Recursive generation!
        if depth > 1:
            for vert in self._adjacents:
                vert.generate(depth-1)
                
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
        text(str(self._state), -6, 6, 16)
        
        # Draw line pointing in direction of `heading`
        stroke(0, 255, 0)
        line(0, 0, 30 * cos(self._heading), 30 * sin(self._heading))
        popMatrix()
        
@definePolytope
class Face(Duals):
    """
    Faces are the dual of Vertices
    The game mostly takes place on faces
    (noteable exception being the Dual Dimension (TODO))
    """
    
    def __init__(self, biome, position, heading_, state):
        """
        `state` is the SigmaSwaps-relevant pair
        """
        Duals.__init__(self, Face, biome, position, heading_, state)
        self._friends = set({})
        self._adjacents = set({})
        self._goal_friends = self.getSides()
        
        Polytope.all_polytopes[Face].add(self)
        
    def getSides(self):
        return self._biome.getSides(*(self._state))
    
    def addAdjacent(self, adj):
        """
        Note that this is NOT mutual
        """
        if adj is not None:
            self._adjacents.add(adj)
            
    def addFriend(self, friend):
        """
        Note that this is NOT mutual
        """
        if friend is not None:
            self._friends.add(friend)
            
    def fullyGenerate(self):
        """
        Generate all friend vertices!
        """
        loop_count = 0
        while self.isPartiallyGenerated():
            assert loop_count < 100, "Something went wrong - stuck in an infinite generation loop!"
            loop_count += 1
            for friend in self._friends:
                #if friend.isPartiallyGenerated(): # < - for some reason, doesn't work with this condition.  TODO: why?
                friend.generate(depth=2)
    
    def highlight(self):
        if self.getAttributes().isPassable():
            self.drawTile(0, color(255, 255, 0, 100))
        else:
            self.drawTile(0, color(255, 0, 0, 100))
            
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
        irregularPolygon(
            [0, 0],
            [
                [
                    x.getPosition()[0] - self._position[0],
                    x.getPosition()[1] - self._position[1]
                ]
                for x in self.getMonotonic(self._friends)
            ],
            self._attributes.getColor(),
            self._attributes.getStroke()
        )
        if highlight is not None:
            irregularPolygon(
                [0, 0],
                [
                    [
                        (x.getPosition()[0] - self._position[0]) * 0.5,
                        (x.getPosition()[1] - self._position[1]) * 0.5
                    ]
                    for x in self.getMonotonic(self._friends)
                ],
                highlight,
                self._attributes.getStroke()
            )
        popMatrix()
        if DRAW_VERTICES:
            for vert in self._friends:
                vert.drawVertex()
        if depth > 1:
            for adj in self._adjacents:
                if adj is not None:
                    adj.drawTile(depth - 1)
