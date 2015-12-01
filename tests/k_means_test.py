import unittest
import random
import collections
from hew import KMeans

def random_point(d=2):
    return tuple([random.uniform(-1, 1) for _ in range(d)])

def init_board(n, d=2):
    return [random_point(d) for i in range(n)]

def init_board_gauss(n, k, d=2):
    n0 = n // k
    X = []
    for i in range(k):
        MU = random_point(d)
        sigma = random.uniform(0.05,0.33)
        for _ in range(n0):
            x = tuple([random.gauss(MU[axis],sigma) for axis in range(d)])
            X.append(x)
    return X

class Test_k_means(unittest.TestCase):
    def test_smoke(self):
        X = init_board_gauss(2000, 6, 6)
        target = KMeans(6, X)
        self.assertEqual(len(X), len(target))
        self.assertEqual(6, target.k)

    def test_tooManyRequestedClusters(self):
        X = [(0, 0, 1)] * 12
        with self.assertRaises(ValueError):
            target = KMeans(2, X)

    @unittest.skip('used for debugging command line')
    def test_commandLine(self):
        args = collections.namedtuple("Parsed", 'input clusters resultColumn outputFileName fields')
        args.input = r'C:\Users\jfarley.15T-5CG3332ZD5\Documents\Personal\uw_in.txt'
        args.clusters = 10
        args.resultColumn = 'Cluster'
        args.outputFileName = r'C:\Users\jfarley.15T-5CG3332ZD5\Documents\Personal\uw_clustered.txt'
        args.fields = ['energy','n_bpm']
        #args.fields = ['acousticness','danceability','energy','instrumentalness',
        #               'liveness','speechiness','valence', 'n_bpm']
        KMeans.run(args)

if __name__ == '__main__':
    unittest.main()
