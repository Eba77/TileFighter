from Polytope import *
from HelperTools import *

"""
`Objects.py`

All non-grid, non-UI things that can be interacted with.
Basically; players, enemies, and obstacles.
Attacks such as swipes and arrows are included here too.
"""

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
        if not destination.getAttributes().isPassable():
            # Can't move if not onto a passable tile!
            return
        else:
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
    
class StabAttack(TileBound, Animation):
    def __init__(self, pos, target_pos, weilder):
        TileBound.__init__(self, pos)
        self._weilder = weilder
        self._is_moving = True
        self._center = pos
        self._target = target_pos
        difference = [
            self._target[0] - self._center[0],
            self._target[1] - self._center[1]
        ]
        self._length = square_dist(self._target, self._center)
        self._angle_to_face = atan2(difference[1], difference[0])
        self._move_steps = (self._length * i * 1.0 / self._move_time for i in range(1, self._move_time + 1))
        
    def continuousUpdate(self):
        """
        Used for animation stuff, TileBounds should not
        have logic based on this
        """
        if not self._is_moving:
            return
        try:
            self._length = next(self._move_steps)
        except StopIteration:
            self._is_moving = False
            self._weilder._is_moving = False
            self._weilder._attack = None
            
    def drawObject(self):
        pushMatrix()
        translate(*(self._center))
        rotate(self._angle_to_face)
        
        # First we draw the overall arc of the stab
        stroke(0, 200, 255, 200)
        fill(0, 200, 255, 100)
        arc(0, 0, 2 * self._length, 2 * self._length, -PI / 2, PI / 2)
        
        # And now the actual sword
        stroke(0, 255, 255, 255)
        line(0, 0, self._length, 0)
        
        popMatrix()
    
        
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
            self._is_moving = False
            self._weilder._is_moving = False
            self._weilder._attack = None
            
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
