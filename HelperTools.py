"""
`HelperTools.py`

Implements all of the methods that I feel should be builtins, but aren't
And also all numpy methods I would want but cannot use due to Java base
"""

import itertools

class cacher:
    """
    For efficiency, we want to cache certain function calls
    so that they don't need to be recomputed every time!
    
    Doesn't work if there are kwargs
    Should only be used on instance and class methods
    (as doesn't cache first arg directly, but as a string)
    
    Python 3.8 has similar function in standard library...
    but this is 2.7 :/
    ^^^ Actually I believe I've now developed this to be
    more powerful than the one in the standard library,
    so yay for that
    Probably doesn't handle edge cases as well though
    """
    def __init__(self, ignore_kwargs = False):
        self._dict = dict({})
        self._ignore_kwargs = ignore_kwargs
        
    def __call__(self, func):
        def cached_func(s, *args, **kwargs):
            if self._ignore_kwargs:
                index = (str(s), args)
            else:
                index = (str(s), args, tuple(kwargs.items()))
            if index not in self._dict:
                # Note that in Python 2, .items() returns list of tuples
                # This is not true in Python 3
                output = func(s, *args, **kwargs)
                if isinstance(output, DONT_CACHE):
                    # Don't cache the output!
                    return output.getValue()
                elif isinstance(output, CACHE_IF) and not output.shouldCache():
                    return output.getValue()
                else:
                    self._dict[index] = output
            return self._dict[index]
        return cached_func
    
class cacheflags:
    """
    If the return value of a to-be-cached function is wrapped in one
    of these, special handling will result.
    
    Note that if an output has already been cached, these won't do anything,
    the function will always return what was already cached
    """
    def __init__(self, val):
        self._val = val
            
    def getValue(self):
        return self._val
    
class DONT_CACHE(cacheflags):
    """
    Wrap output values in this to prevent them being cached
    """
    def __init__(self, val):
        cacheflags.__init__(self, val)
        
class CACHE_IF(cacheflags):
    """
    Only cache once the output equals some `compare` value
    or satisfies some `function`
    """
    def __init__(self, val, compare=None, function=None):
        assert compare or function, "Has to be in either compare mode, or function mode!"
        cacheflags.__init__(self, val)
        if compare is not None:
            self._should_cache = val == compare
        else:
            self._shoulld_cache = function(val)

    def shouldCache(self):
        return self._should_cache

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
    # TODO: I think processing has `dist` as a builtin?
    return sum([(x-y)**2 for x, y in zip(pos_1, pos_2)])

# Taken from processing tutorial, modified greatly
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
        # Needed for triangles, I'm just guessing this generalizes
        # to odd-sided shapes; doesn't really matter, 'cuz no
        # k-uniform tiling will ever use odd non-triangle shapes
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
    
    
def irregularPolygon(pos, points, in_fill = None, in_stroke = None):
    """
    Draws an irregular polygon with vertices at `points`
    Warning; doesn't work for nonconvex polygons
    """
    pushMatrix()
    translate(*pos)
    beginShape()
    if in_fill is not None:
        fill(in_fill)
    if in_stroke is not None:
        stroke(in_stroke)
    for p in points:
        vertex(*p)
    endShape(CLOSE)
    popMatrix()
    
def evenOddRule(pos, points):
    """
    By checking the Even-Odd Rule, we can determine
    whether or not `pos` lies in the convex polygon defined
    by `points`!
    This is taken from Wikipedia https://en.wikipedia.org/wiki/Even%E2%80%93odd_rule
    """
    num = len(points)
    i = 0
    j = num - 1
    c = False
    x, y = pos[0], pos[1]
    for i in range(num):
        if (((points[i][1] > y) != (points[j][1] > y))
          and (x < points[i][0] + (points[j][0] - points[i][0]) * (y - points[i][1]) / (points[j][1] - points[i][1]))):
            c = not c
        j = i
    return c
    
