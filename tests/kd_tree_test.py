import sys
import unittest
import math
from random import random
from hew import KDTree
from hew.structures.kd_tree import square_distance

if sys.version >= '3':
    xrange = range

class Test_KDTree(unittest.TestCase):
    def test_smoke(self):
        k = 5
        npoints = 1000
        lookups = 1000
        eps = 1e-8
    
        points = [(tuple(random() for _ in xrange(k)), i)
                  for i in xrange(npoints)]

        tree = KDTree(points)

        for _ in xrange(lookups):
        
            destination = [random() for _ in xrange(k)]
            _, _, mindistance = tree.nearest_neighbor(destination)
        
            minsq = min(square_distance(p, destination) for p, _ in points)
            self.assertLess(abs(math.sqrt(minsq) - mindistance), eps)

if __name__ == '__main__':
    unittest.main()