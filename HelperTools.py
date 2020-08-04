"""
`HelperTools.py`

Implements all of the methods that I feel should be builtins, but aren't
And also all numpy methods I would want but cannot use due to Java base
"""

import itertools

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
