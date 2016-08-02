import sys
if sys.version >= '3':
    xrange = range

# -----------------------------------------------------------------------------


class MonteCarlo(object):
    def __init__(self, mins=None, maxs=None):
        if not mins:
            mins = [-1, -1]

        if not maxs:
            maxs = [1, 1]

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
