"""
`TileAttributes.py`
Wraps the TileAttribute class
"""

import random as rnd

class TileAttribute:
    """
    Just like how some blocks in Minecraft are grass or wood,
    this class concerns the actual type of tile that a Tile is.
    """
    
    def __init__(self):
        self._color = color(255)
        self._stroke = color(0)
        
    def getColor(self):
        return self._color
    
    def getStroke(self):
        return self._stroke
    
    def isPassable(self):
        raise NotImplementedError
        
    def isDestructible(self):
        return False
    
    def isStabDestructible(self):
        return False
    
    def destroy(self):
        raise NotImplementedError
        
class MetaTile(TileAttribute):
    """
    Parent class to meta-ified biomes.
    """
    def __init__(self, biome):
        TileAttribute.__init__(self)
        self._biome = biome
        
    def __eq__(self, other):
        return self._biome == other._biome
    
                    
class Passable(TileAttribute):
    """
    A tile that standard TileBounds can pass through
    """
    
    def __init__(self):
        TileAttribute.__init__(self)
        
    def isPassable(self):
        return True
    
class Impassable(TileAttribute):
    """
    Opposite of Passable, standard TileBounds can't pass
    """
    
    def __init__(self):
        TileAttribute.__init__(self)
        
    def isPassable(self):
        return False
    
class Destructible(Impassable):
    """
    Anything that can be destroyed by some method
    `to_what` is the tile left behind after destruction
    """
    
    def __init__(self, to_what):
        TileAttribute.__init__(self)
        self._to_what = to_what
        
    def isDestructible(self):
        return True
    
    def destroy(self):
        return self._to_what
    
class StabDestructible(Destructible):
    """
    Anything that can be destroyed by the player's stab attack
    """
    
    def __init__(self, to_what):
        Destructible.__init__(self, to_what)
        
    def isStabDestructible(self):
        return True
    
class BlankTile(Passable):
    """
    Default tile, should not show up in final game
    """
    
    def __init__(self):
        Passable.__init__(self)
        self._color = color(255)
        self._stroke = color(0)
        
class UnloadedTile(BlankTile):
    """
    Tile that faces will be if they're not fully loaded!
    """
    
    def __init__(self):
        BlankTile.__init__(self)
        
class HexForestGrass(Passable):
    """
    Simple grass, comes in three colors chosen at random.
    No special properties
    """
    
    def __init__(self):
        Passable.__init__(self)
        self._color = rnd.choice([color(0, 150, 0, 255), color(40, 120, 0, 255), color(0, 190, 0, 255)])
        self._stroke = color(0)
        
class HexForestTree(StabDestructible):
    """
    Simple tree
    Can't be passed through, can be cut down
    TODO: Make able to be cut down
    """
    
    def __init__(self):
        StabDestructible.__init__(self, HexForestGrass())
        self._color = color(30) # TODO: Better display choice
        self._stroke = color(0)
        
class FancyFloor(Passable):
    """
    Just another flavor of basic tile, colors chosen at random from set
    """
    def __init__(self):
        Passable.__init__(self)
        self._color = rnd.choice([color(255, 200, 0, 255), color(255, 0, 0, 255)])
        self._stroke = color(0)
        
class FancyFoliage(Passable):
    """
    Just another flavor of basic tile, colors chosen at random from set
    """
    def __init__(self):
        Passable.__init__(self)
        self._color = rnd.choice([color(161, 199, 37 + 20 * i, 255) for i in range(6)])
        self._stroke = color(0)
