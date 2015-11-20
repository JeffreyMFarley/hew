import sys
import unittest
import math
from random import random
from hew import KDTree
from hew.structures.math import Vector

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
        
            minsq = min(Vector.square_distance(p, destination) 
                        for p, _ in points)
            self.assertLess(abs(math.sqrt(minsq) - mindistance), eps)


    def test_fromTable(self):
        table = [
                 {'x': 0.3, 'y': 0.4, 'z': 0.5, 'name': 'foo', 'desc': 'bar'}, 
                 {'x': 0.5, 'z': 0.9, 'name': 'baz', 'desc': 'qaz'}, 
                 {'x': 0.2, 'y': 0.8, 'z': 0.2, 'desc': 'den'}, 
                ]
        
        tree = KDTree.fromTable(table, ['x', 'y', 'z'], ['name', 'desc'])
        points, labels, distance = tree.nearest_neighbor([0.1, 1, 0.1])
        self.assertEqual(points[0], 0.2)
        self.assertEqual(points[1], 0.8)
        self.assertEqual(points[2], 0.2)
        self.assertEqual(labels[0], '')
        self.assertEqual(labels[1], 'den')
        self.assertTrue(0.2 < distance < 0.25)

if __name__ == '__main__':
    unittest.main()