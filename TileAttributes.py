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
        return to_what
    
class StabDestructible(Destructible):
    """
    Anything that can be destroyed by the player's stab attack
    """
    
    def __init__(self, to_what):
        Destructible.__init__(self, to_what)
        
    def isStabDestructible(self):
        return True
        
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
        StabDestructible.__init__(self, HexForestGrass)
        self._color = color(30) # TODO: Better display choice
        self._stroke = color(0)
