"""
`MagicNumbers.py`

All global constants are here
"""

DRAW_VERTICES = True
DRAW_EDGES = True
DRAW_FACES = True
LENIENT = True # Some things that fail asserts or raise NotImplementedErrors will fail gracefully
CLOSENESS_CONSTANT = 1 # how close two tiles have to be to be considered the same
BIOME_SIZE = 1000 # Radius of Biome Tilings
# ^^^ (note that since biome tilings use the dual, this does not directly correspond to actual radii,
# but it is linearly related)
TILE_SIZE = 100 # Radius of Tile Tilings
DESIRED_FRAME_RATE = 60
DEBUG_VERTICES = False # Whether or not to show debug info on vertices
VERSION = "0.3c [Alpha]"
DEBUG_RENDERER = False
