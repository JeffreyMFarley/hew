import sys

try:
    from itertools import izip
except ImportError:  #python3.x
    izip = zip

if sys.version >= '3':
    xrange = range

# -----------------------------------------------------------------------------

class Vector:
    @classmethod
    def bounds(cls, vectors):
        """ Determines the minimum an maximum dimensions"""
        d = len(vectors[0])
        mins = [float("inf")] * d
        maxs = [-float("inf")] * d
        for x in vectors:
            for i, v in enumerate(x):
                if v < mins[i]:
                    mins[i] = v
                if v > maxs[i]:
                    maxs[i] = v

        return mins, maxs

    @classmethod
    def mean(cls, vectors):
        """ Centroid of the vectors """
        d = len(vectors[0])
        c = [0.] * d
        n = len(vectors)
        for x in vectors:
            for i, v in enumerate(x):
                c[i] += v
        for i in xrange(d):
            c[i] /= n
        return c

    @classmethod
    def square_distance(cls, a, b):
        s = 0
        for x, y in izip(a, b):
            d = x - y
            s += d * d
        return s
 