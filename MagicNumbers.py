"""
`MagicNumbers.py`

All global constants are here
"""

DRAW_VERTICES = True
DRAW_EDGES = True
LENIENT = True # Some things that fail asserts or raise NotImplementedErrors will fail gracefully
CLOSENESS_CONSTANT = 1 # how close two tiles have to be to be considered the same
BIOME_SIZE = 1000 # Side Length of Biome Tilings
# ^^^ (note that since biome tilings use the dual, this does not directly correspond to actual side lengths,
# but larger numbers will linearly increase the apothem, which is linearly related to the side length of the dual,
# and thus increasing this will have a linear affect on biome size)
TILE_SIZE = 100 # Side Length of Tile Tilings
VERSION = "0.3a [Alpha]"
