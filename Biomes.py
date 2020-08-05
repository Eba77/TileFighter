# -*- coding: utf-8 -*-
"""
`Biomes.py`
This file contains everything to do with the macro-scale terrain generation
(the only aspect of terrain generation not under its control is the fine
 details of how tilings are done, which are either in `Geometry.py` or
 `Polytope.py`)
"""

from Geometry import *
from TileAttributes import *
from MagicNumbers import *
import random as rnd

class Biome:
    cur_id = 0
    
    def __init__(self, v_conf, n, col):
        self._biome_id = Biome.cur_id
        self._vertex_configuration = v_conf
        self._name = n
        self._colors = col
        self._base_radius = [100] * len(v_conf)
        Biome.cur_id += 1
  
    def getSides(self, v, e):
        return self._vertex_configuration[v][e]
  
    def getTileNumAtVertex(self, v):
        """
        v is the vertex type
        """
        return len(self._vertex_configuration[v])
  
    def getBiomeName(self):
        return self._name
    
    def getTileColor(self, position_in_vertex):
        return self._colors[position_in_vertex[1]]
    
    def __eq__(self, other):
        return self._biome_id == other._biome_id
    
    def getSideLength(self, v, e):
        """
        Gets the length of the side of the polygon
        The side length is constant throughout the biome, and
        is based on the first tile in the vertex configuration
        """
        return 2 * self.getRadius(v, 0) * sin(self.getTurningAngle(v, 0) / 2)
    
    def getRadius(self, v, e):
        """
        Calculates radius of tile at position n in config
        under the assumption that the first listed tile has radius `_base_radius`
        """
        if e == 0:
            return self._base_radius[v]
        return self.getSideLength(v, e) / (2 * sin(self.getTurningAngle(v, e) / 2))
    
    def getTurningAngle(self, v, e):
        """
        Angle at center of tile in any triangle with center as vertex and then
        the other two vertices resting on a single side of the polygon
        (so for example a square should have 90°, hexagon should have 60°)
        """
        return TWO_PI / self._vertex_configuration[v][e]
    
    def getVertexAngle(self, v, e):
        """
        Get angle that the two edges of the nth polygon located at this vertex form
        TODO: This does not work for spherical/hyperbolic geometry, fix that!
        (Doesn't work because it relies on triangle angles adding up to PI radians)
        """
        return PI - self.getTurningAngle(v, e)
    
    def swap(self, v, e):
        return self._vertex_configuration.swap(v, e)
    
    def getAngleOffset(self, v, e):
        return sum([self.getTurningAngle(v, _e) for _e in range(e + 1)])
    
    def getTileAttributes(self, sides):
        """
        Returns a TileAttribute instance
        """
        if LENIENT:
            return BlankTile()
        else:
            raise NotImplementedError
    
class HEX_FOREST(Biome):
    
    def __init__(self):
        Biome.__init__(self, VertexConfiguration([[6] * 3]), "Hex Forest", [color(0, 150, 0, 255), color(40, 120, 0, 255), color(0, 190, 0, 255)])
        
    def getTileAttributes(self, sides):
        """
        Returns a TileAttribute instance
        Either HexForestGrass or HexForestTree
        """
        rnd_gen = rnd.random()
        if rnd_gen < 0.9:
            return HexForestGrass()
        else:
            return HexForestTree()

class PLEASANT_PLAINS(Biome):
    
    def __init__(self):
        Biome.__init__(self, VertexConfiguration([[4] * 4]), "Pleasant Plains", [color(255, 200, 0, 255), color(255, 0, 0, 255)] * 2)
        
    def getTileAttributes(self, sides):
        """
        Always FancyFloor
        """
        return FancyFloor()

class DANGEROUS_DESERT(Biome):
    
    def __init__(self):
        Biome.__init__(self, VertexConfiguration([[3] * 6]), "Dangerous Desert", [color(161, 199, 37 + 20 * i, 255) for i in range(6)])

class TEST_8_8_4(Biome):
    
    def __init__(self):
        Biome.__init__(self, VertexConfiguration([[8, 8, 4]]), "???", [color(150, 150, 0, 255)] * 3)

class TEST_4_6_12(Biome):
    
    def __init__(self):
        Biome.__init__(self, VertexConfiguration([[4, 6, 12]]), "???", [color(255, 255, 255, 255)] * 3)

class TEST_4_3_4_3_3(Biome):
    
    def __init__(self):
        Biome.__init__(self, VertexConfiguration([[4, 3, 4, 3, 3]]), "???", [color(255, 255, 255, 255)] * 5)

class TEST_3_3_3_4_4(Biome):
    
    def __init__(self):
        Biome.__init__(self, VertexConfiguration([[3, 3, 3, 4, 4]]), "???", [color(255, 255, 255, 255)] * 5)

class TEST_3_3_3_3_6(Biome):
    
    def __init__(self):
        Biome.__init__(self, VertexConfiguration([[3, 3, 3, 3, 6]] * 2), "???", [color(255, 255, 255, 255)] * 5)
        # ^^^ Chiral, so I used the vertex mirroring trick, hence why it looks 2-uniform; it is really 1-uniform

class TEST_3_6_3_6(Biome):
    
    def __init__(self):
        Biome.__init__(self, VertexConfiguration([[3, 6, 3, 6]]), "???", [color(255, 255, 255, 255)] * 4)

class TEST_3_4_6_4(Biome):
    
    def __init__(self):
        Biome.__init__(self, VertexConfiguration([[3, 4, 6, 4]]), "???", [color(255, 255, 255, 255)] * 4)

class TEST_3_12_12(Biome):
    
    def __init__(self):
        Biome.__init__(self, VertexConfiguration([[3, 12, 12]]), "???", [color(255, 255, 255, 255)] * 3)

class TEST_3_3_3_3_3_3_and_3_4_3_4_3(Biome):
    
    def __init__(self):
        Biome.__init__(self, VertexConfiguration([[3] * 6, [3, 4, 3, 4, 3]]), "???", [color(255, 255, 255, 255)] * 6)
