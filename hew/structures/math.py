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

# -----------------------------------------------------------------------------

class MonteCarlo:
    def __init__(self, mins=[-1, -1], maxs=[1, 1]):
        assert len(mins) == len(maxs)
        assert len(mins) > 0
        self.dim = len(mins)
        self.mins = list(mins)
        self.maxs = list(maxs)

    def xrange(self, N):
        import random

        for _ in xrange(N):
            yield tuple([random.uniform(self.mins[d], self.maxs[d]) 
                         for d in range(self.dim)])

# -----------------------------------------------------------------------------

class RunningStatistics:
    def __init__(self):
        self.reset()

    def reset(self):
        self.count = 0
        self.sum = 0
        self.square_sum = 0
        self.min = float("inf")
        self.max = -float("inf")

    @property
    def mean(self):
        return self.sum / self.count if self.count > 0 else 0

    @property
    def variance(self):
         if self.count < 1:
             return 0
         
         return (self.square_sum - 
                ((self.sum * self.sum) / self.count)
                ) / (self.count - 1)

    @property
    def standard_deviation(self):
        import math
        return math.sqrt(self.variance)

    def __iadd__(self, value):
        self.count += 1;
        self.sum += value;
        self.square_sum += (value * value);

        if value < self.min:
            self.min = value;

        if value > self.max:
            self.max = value;

        return self

    def __isub__(self, value):
        if self.count < 1:
            return

        self.count -= 1;
        self.sum -= value;
        self.square_sum -= (value * value);

        return self
