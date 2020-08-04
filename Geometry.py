"""
`Geometry.py`
This handles the details of vertex configurations and their transformations
"""

class SigmaSwaps:
    def __init__(self, swap_dict):
        """
        Takes in the swapping graph (represented as a dict)
        """
        self._swaps = swap_dict
        
    def __call__(self, input_state):
        """
        Performs transformation on (vert_info, edge_info) pairs
        """
        return self._swaps[input_state]
    
    @classmethod
    def getIdentity(cls, how_many):
        """
        Takes a number, returns dict mapping (0, n) to itself, up to n=how_many-1
        """
        to_return = dict({})
        for n in range(how_many):
            to_return[(0, n)] = (0, n)
        return SigmaSwaps(to_return)
        
    
class VertexConfiguration:
    """
    Mathematical representation of vertex configurations
    6.6.6 would be 3 hexagons per vertex,
    4.4.4.4 would be 4 squares per vertex
    5.5 would be 2 pentagons per vertex (would induce spherical geometry)
    6^3 is another way to express 6.6.6
    6^3.4 would be 3 hexagons and then a square
    6.4.4.6 is not the same as 6.4.6.4 == (6.4)^2
    [3^6; (3.4)^2.3] is a 2-uniform tiling, each vertex belongs
    to one of two configs listed above
    """
    
    def __init__(self, raw_config):
        self._raw_config = raw_config
        self._sigma_swaps = self.calculateSigmaSwaps()
        
    def __len__(self):
        return len(self._raw_config)
    
    def __getitem__(self, n):
        return self._raw_config[n]
    
    def calculateSigmaSwaps(self):
        """
        Assuming sinewise orientation, this represents the mapping of edges
        to edges between adjacent vertices.
        As an example, the 3^3@4^2 tiling's "zeroth" edge (horizontal rightwards)
        gets mapped to the third edge of the vertex connected by said edge
        Hard to explain non-graphically
        """
        # I don't know how to calculate this, so I'm adding a placeholder value
        if self._raw_config == [[8, 8, 4]]:
            return SigmaSwaps.getIdentity(3)
        elif self._raw_config == [[4, 3, 4, 3, 3]]:
            to_return = dict({})
            to_return[(0, 0)] = (0, 2)
            to_return[(0, 1)] = (0, 3)
            to_return[(0, 2)] = (0, 0)
            to_return[(0, 3)] = (0, 1)
            to_return[(0, 4)] = (0, 4)
            return SigmaSwaps(to_return)
        elif self._raw_config == [[3, 3, 3, 3, 6]] * 2:
            """
            3.3.3.3.6 is chiral
            This, I believe, is the cause of it being hard to work with
            It basically has to be treated as a 2-uniform tiling, even though
            each vertex is functionally the same.
            To get the other chirality, I expect I just have to swap which vertex is
            the '0' vertex and which one is the '1' vertex
            I also suspect this trick of 2-uniformifying should work on all chiral k-uniform tilings;
            It will be much more complex and may result in doubling k, but creating 'mirror' vertices
            is probably a good strategy, especially since the whole problem comes about due to a lack
            of mirror reflections!
            """
            to_return = dict({})
            to_return[(0, 0)] = (1, 0)
            to_return[(0, 1)] = (1, 2)
            to_return[(0, 2)] = (1, 3)
            to_return[(0, 3)] = (1, 1)
            to_return[(0, 4)] = (1, 4)
            to_return[(1, 0)] = (0, 0)
            to_return[(1, 1)] = (0, 3)
            to_return[(1, 2)] = (0, 1)
            to_return[(1, 3)] = (0, 2)
            to_return[(1, 4)] = (0, 4)
            return SigmaSwaps(to_return)
        elif self._raw_config == [[3, 3, 3, 4, 4]]:
            to_return = dict({})
            to_return[(0, 0)] = (0, 0)
            to_return[(0, 1)] = (0, 2)
            to_return[(0, 2)] = (0, 1)
            to_return[(0, 3)] = (0, 3)
            to_return[(0, 4)] = (0, 4)
            return SigmaSwaps(to_return)
        elif self._raw_config == [[4, 6, 12]]:
            return SigmaSwaps.getIdentity(3)
        elif self._raw_config == [[3, 6, 3, 6]]:
            return SigmaSwaps.getIdentity(4)
        elif self._raw_config == [[3, 4, 6, 4]]:
            return SigmaSwaps.getIdentity(4)
        elif self._raw_config == [[3, 12, 12]]:
            return SigmaSwaps.getIdentity(3)
        elif self._raw_config == [[3] * 6, [3, 4, 3, 4, 3]]:
            to_return = dict({})
            for n in range(6):
                to_return[(0, n)] = (1, 0)
            to_return[(1, 0)] = (0, 0)
            to_return[(1, 1)] = (1, 1)
            to_return[(1, 2)] = (1, 2)
            to_return[(1, 3)] = (1, 3)
            to_return[(1, 4)] = (1, 4)
            return SigmaSwaps(to_return)
        else:
            assert len(self._raw_config) == 1, "k-uniform tilings need explicit dict creation!"
            return SigmaSwaps.getIdentity(len(self._raw_config[0]))
    
    def swap(self, v, e):
        return self._sigma_swaps((v, e))
