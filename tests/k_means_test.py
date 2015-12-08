import unittest
import random
import collections
from hew import KMeans

def random_point(d=2):
    return tuple([random.uniform(-1, 1) for _ in range(d)])

def init_board_gauss(n, k, d=2):
    n0 = n // k
    X = []
    for i in range(k):
        mu = random_point(d)
        sigma = random.uniform(0.05,0.33)
        for _ in range(n0):
            x = tuple([random.gauss(mu[axis],sigma) for axis in range(d)])
            X.append(x)
    return X

def init_4_clusters(n=200):
    MU = [(-0.5, -0.5), (0.5, 0.5), (-0.5, 0.5), (0.5, -0.5)]
    k = len(MU)
    d = len(MU[0])
    sigma = 0.1

    n0 = n // k
    X = []
    for i, mu in enumerate(MU):
        for _ in range(n0):
            x = tuple([random.gauss(mu[axis],sigma) 
                        for axis in range(d)])
            X.append(x)
    return X

# -----------------------------------------------------------------------------

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

    def test_optimal_clusters(self):
        from hew.clusters.k_means import optimal_clusters

        X = init_4_clusters(400)
        actual = optimal_clusters(X)
        self.assertEqual(4, actual)

    def test_kmeans_plus_plus(self):
        from hew.clusters.k_means import kmeans_plus_plus

        X = init_4_clusters()
        actual = kmeans_plus_plus(X, 4)

        found = [False] * 4
        for a in actual:
            if a[0] < 0 and a[1] < 0:
                found[0] = True
            elif a[0] > 0 and a[1] > 0:
                found[1] = True
            elif a[0] < 0 and a[1] > 0:
                found[2] = True
            elif a[0] > 0 and a[1] < 0:
                found[3] = True
        self.assertTrue(all(found))

    def test_lloyds(self):
        from hew.clusters.k_means import lloyds_algorithm

        X = init_4_clusters()
        centroids = [(-0.75, -0.75), (0.75, 0.75), (-0.75, 0.75), (0.75, -0.75)]

        actual, clusters, iterations = lloyds_algorithm(X, centroids)

        self.assertAlmostEqual(actual[0][0], -0.5, 1)
        self.assertAlmostEqual(actual[0][1], -0.5, 1)
        self.assertAlmostEqual(actual[1][0], 0.5, 1)
        self.assertAlmostEqual(actual[1][1], 0.5, 1)
        self.assertAlmostEqual(actual[2][0], -0.5, 1)
        self.assertAlmostEqual(actual[2][1], 0.5, 1)
        self.assertAlmostEqual(actual[3][0], 0.5, 1)
        self.assertAlmostEqual(actual[3][1], -0.5, 1)

    unittest.skip('used for debugging command line')
    def test_commandLine(self):
        args = collections.namedtuple("Parsed", 'input clusters resultColumn outputFileName fields')
        args.input = r'C:\Users\jfarley.15T-5CG3332ZD5\Documents\Personal\mbm.txt'
        args.clusters = -1
        args.resultColumn = 'Cluster'
        args.outputFileName = r'C:\Users\jfarley.15T-5CG3332ZD5\Documents\Personal\mbm_clustered.txt'
        args.fields = ['energy', 'instrumentalness']
        #args.fields = ['instrumentalness','speechiness','valence', 'n_bpm']
        #args.fields = ['acousticness','danceability','energy','instrumentalness',
        #               'liveness','speechiness','valence', 'n_bpm']
        KMeans.run(args)

if __name__ == '__main__':
    unittest.main()
