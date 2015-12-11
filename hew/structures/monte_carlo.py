import sys
if sys.version >= '3':
    xrange = range

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

