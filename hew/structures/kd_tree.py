import collections
import math
from hew.structures.math import Vector

# -----------------------------------------------------------------------------
# Adapted from: 
# http://code.activestate.com/recipes/577497-kd-tree-for-nearest-neighbor-search-in-a-k-dimensi/
# -----------------------------------------------------------------------------

KDNode = collections.namedtuple("KDNode", 'point axis label left right')

class KDTree(object):
    """A tree for nearest neighbor search in a k-dimensional space."""

    # -------------------------------------------------------------------------
    # Initializer
    # -------------------------------------------------------------------------
    def __init__(self, objects):
        """`objects` is an iterable of (vector, label) tuples"""

        a = list(objects)
        assert len(a) > 0
        assert len(a[0]) == 2

        self.k = len(a[0][0])

        def build_tree(objects, axis=0):

            if not objects:
                return None

            objects.sort(key=lambda o: o[0][axis])
            median_idx = len(objects) // 2
            median_point, median_label = objects[median_idx]

            next_axis = (axis + 1) % self.k
            return KDNode(median_point, axis, median_label,
                        build_tree(objects[:median_idx], next_axis),
                        build_tree(objects[median_idx + 1:], next_axis))

        self.root = build_tree(a)

    # -------------------------------------------------------------------------
    # Public Methods
    # -------------------------------------------------------------------------
    
    @classmethod
    def fromTable(cls, arrayOfDictionaries, pointFields, labelFields):
        """ Builds a k-d tree from a tabular structure """
        pairs = []
        for o in arrayOfDictionaries:
            points = [float(o[f]) if f in o else 0. for f in pointFields]
            labels = [o[f] if f in o else '' for f in labelFields]
            pairs.append((points, labels))

        return KDTree(pairs)

    def nearest_neighbor(self, destination):
        """`destination` is a vector of length `k`

        Returns:
            (closest point, closest label, distance)
        """
        assert len(destination) == self.k

        best = [None, None, float('inf')]
        # state of search: best point found, its label,
        # lowest squared distance

        def recursive_search(here):

            if here is None:
                return
            point, axis, label, left, right = here

            here_sd = Vector.square_distance(point, destination)
            if here_sd < best[2]:
                best[:] = point, label, here_sd

            diff = destination[axis] - point[axis]
            close, away = (left, right) if diff <= 0 else (right, left)

            recursive_search(close)
            if diff ** 2 < best[2]:
                recursive_search(away)

        recursive_search(self.root)
        return best[0], best[1], math.sqrt(best[2])

if __name__ == '__main__':
    pass
