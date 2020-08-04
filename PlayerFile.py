"""
`PlayerFile.py`
Code specific to the player.
"""

from Objects import *

class Player(TileBound):
    MAX_SWIPE_DIST = 250
    
    def __init__(self, pos):
        TileBound.__init__(self, pos)
        self._attack = None
        
    def move(self, destination):
        if not destination.isAdjacent(self.getTileOn()):
            # Can only move to adjacent tiles!
            return
        if destination.getAttributes().isStabDestructible():
            # We can destroy it!
            self.stab(destination.getPosition())
        else:
            # We'll try to move
            TileBound.move(self, destination)
        
    def stab(self, where):
        """
        Triggers the player's stab attack
        """
        if self._is_moving:
            return
        # This is considered a 'move', so we have to set movement variables
        # to reasonable values.  `_move_steps` is set to forever give
        # the same position, so that no real moving happens.
        self._is_moving = True
        self._move_steps = (self._position for x in itertools.count())
        self._attack = StabAttack(self._position, where, self)
        
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
        self._attack = SwipeAttack(self._position, self, swipe_length)
        
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
