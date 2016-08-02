import sys
import csv
import random
import argparse


try:
    from itertools import izip
except ImportError:  # python3.x
    izip = zip

if sys.version >= '3':
    xrange = range

# -----------------------------------------------------------------------------
# obj -> obj
# -----------------------------------------------------------------------------


def convertBooleanFields(o):
    for k, v in o.items():
        if v.lower() == 'false':
            o[k] = 0.
        elif v.lower() == 'true':
            o[k] = 1.
        else:
            o[k] = v
    return o

# -----------------------------------------------------------------------------
# Adapted from
# https://datasciencelab.wordpress.com/2013/12/12/clustering-with-k-means-in-python/
# and
# https://gist.github.com/larsmans/4952848
#
# mu :: the center point of a cluster, the centroid
# MU :: array of centroids
# X  :: a set of n points
# x  :: a point vector
# k  :: number of clusters
# d  :: number of dimensions

# -----------------------------------------------------------------------------
# Cluster Algorithms
# -----------------------------------------------------------------------------


def has_converged(A, B):
    return set([tuple(a) for a in A]) == set([tuple(b) for b in B])


# http://rosettacode.org/wiki/K-means%2B%2B_clustering#Python
# https://datasciencelab.wordpress.com/2014/01/15/improved-seeding-for-clustering-with-k-means/
def kmeans_plus_plus(X, k, distance_fn):
    """ Determines `k` centroids from an array of points `X` """

    def min_dist(x, C):
        result = float("inf")
        for c in C:
            d = distance_fn(x, c)
            if d < result:
                result = d
        return result

    l = len(X)
    MU = [None] * k
    dist = [0.] * l

    MU[0] = list(random.choice(X))

    for i in xrange(1, k):
        accum = 0.
        centroids = MU[:i]
        for j, x in enumerate(X):
            dist[j] = min_dist(x, centroids)
            accum += dist[j]

        accum *= random.random()

        for j, d in enumerate(dist):
            accum -= d
            if accum <= 0:
                MU[i] = list(X[j])
                break

    return MU


# https://en.wikipedia.org/wiki/Lloyd%27s_algorithm
def lloyds_algorithm(X, initial_MU, distance_fn):
    """
    `X` is the array of points,
    'initial_MU' is the initial array of centroids
    """
    from hew.structures.vector import centroid

    MU = list(initial_MU)
    l = len(X)
    k = len(MU)
    C = [None] * l
    iterations = 0
    done = False

    while not done:
        old = list(MU)
        iterations += 1

        for i, x in enumerate(X):
            C[i] = min(xrange(k), key=lambda j: distance_fn(x, MU[j]))
        for j, _ in enumerate(MU):
            members = [x for i, x in enumerate(X) if C[i] == j]
            MU[j] = centroid(members)

        done = has_converged(MU, old)

    return MU, C, iterations


# https://datasciencelab.wordpress.com/2013/12/27/finding-the-k-in-k-means-clustering/
def optimal_clusters(X, distance_fn, max_k=10, samples=10):
    """ `X` is the input array of points to test
    `max_k` is the maximum number of clusters to test for
    `samples` is the number of monte carlo simulations to run at each step
    """
    from hew import RunningStatistics, MonteCarlo
    from hew.structures.vector import bounds
    import math

    mins, maxs = bounds(X)
    B_Generator = MonteCarlo(mins, maxs)
    nX = len(X)

    # arrays that include max_k
    Gap = [0.] * (max_k + 1)
    SSD = [0.] * (max_k + 1)
    WK0 = [0.] * (max_k + 1)
    WKB = [0.] * (max_k + 1)

    sys.stderr.write('Checking for optimal cluster size\n')

    for k in range(1, max_k + 1):
        c = KMeans(k, X, distance_fn, True)
        sys.stderr.write('{0} '.format(k))
        sys.stderr.flush()

        s = RunningStatistics()
        for _ in range(samples):
            B = list(B_Generator.xrange(nX))
            b = KMeans(k, B, distance_fn)
            s += math.log(b.Wk)

        WK0[k] = math.log(c.Wk)
        WKB[k] = s.mean
        SSD[k] = s.standard_deviation * math.sqrt(1 + 1/s.count)
        Gap[k] = s.mean - WK0[k]

    sys.stderr.write('\n')

    opt_k = None
    for k in range(1, max_k - 1):
        nextOne = Gap[k+1] - SSD[k+1]
        delta = Gap[k] - nextOne
        if delta > 0 and not opt_k:
            opt_k = k

    return opt_k

# -----------------------------------------------------------------------------


class KMeans(object):
    # -------------------------------------------------------------------------
    # Factory Methods
    # -------------------------------------------------------------------------
    @classmethod
    def fromTable(cls, k, arrayOfDictionaries, vectorFields, distance_fn):
        """ Initializes a k-means instance from a tabular structure """
        vectors = []
        for o in arrayOfDictionaries:
            vectors.append(tuple([float(o[f])
                                  if f in o else 0.
                                  for f in vectorFields]))

        if k == -1:
            k = optimal_clusters(vectors, distance_fn, 20)

        return KMeans(k, vectors, distance_fn, True)

    # -------------------------------------------------------------------------
    # Customization Methods
    # -------------------------------------------------------------------------
    def __init__(self, k, vectors, distance_fn, use_kpp=False):
        """
        `k` is the number of clusters to find
        `vectors` is the array of points
        `distance_fn` a function that calculates the difference between points
        `use_kpp` if True, the initial centroids will be seeded using KMeans++
        """
        assert len(vectors) > 0
        self.distance_fn = distance_fn

        # initialize cluster centers
        if use_kpp:
            MU0 = kmeans_plus_plus(vectors, k,  distance_fn)
        else:
            MU0 = random.sample(set(vectors), k)

        self.vectors = vectors
        self.k = k
        self.d = len(vectors[0])
        self.MU, self.clusterIndex, self.iter = lloyds_algorithm(vectors, MU0,
                                                                 distance_fn)
        self.C = None

    def __len__(self):
        return len(self.clusterIndex)

    def __iter__(self):
        for c in self.clusterIndex:
            yield c

    @property
    def Wk(self):
        """ A measure of the compactness of clustering """
        C = self.groups
        # coeff = [1/(2*len(C[i])) for i in xrange(self.k)]

        return sum([self.distance_fn(self.MU[i], c)  # * coeff[i]
                    for i in range(self.k)
                    for c in C[i]])

    @property
    def groups(self):
        if not self.C:
            self.C = [[] for _ in xrange(self.k)]
            for i, cluster_i in enumerate(self.clusterIndex):
                self.C[cluster_i].append(self.vectors[i])
        return self.C

    # -------------------------------------------------------------------------
    # Useful Methods
    # -------------------------------------------------------------------------

    @classmethod
    def run(cls, args):
        with open(args.input, 'r') as f:
            reader = csv.DictReader(f, dialect=csv.excel_tab)
            out_cols = reader.fieldnames
            data = [convertBooleanFields(row) for row in reader]

        distance_fn = None
        if args.distance == 'euclid':
            from hew.structures.vector import distance_euclid_squared
            distance_fn = distance_euclid_squared
        elif args.distance == 'cosine':
            from hew.structures.vector import distance_cosine_similarity
            distance_fn = distance_cosine_similarity

        k_means = KMeans.fromTable(args.clusters, data, args.fields,
                                   distance_fn)

        with open(args.outputFileName, 'w') as f:
            cells = list(out_cols)
            cells.append(args.resultColumn)
            f.write('\t'.join(cells))
            f.write('\n')

            for orig, cluster in izip(input, k_means):
                cells = [str(orig[x]) for x in out_cols]
                cells.append(str(cluster + 1))
                f.write('\t'.join(cells))
                f.write('\n')

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------


def buildArgParser():
    description = 'Determine clusters from a table of features'
    p = argparse.ArgumentParser(description=description)
    p.add_argument('input', metavar='inputFileName',
                   help='the file to process')
    p.add_argument('-c', '--clusters', default=-1, type=int,
                   help='the number of clusters')
    p.add_argument('-r', '--results', dest='resultColumn',
                   default='cluster',
                   help='the column that holds the result')
    p.add_argument('-o', '--output', dest='outputFileName',
                   default='clusters.txt',
                   help='the name of the file that will hold the results')
    p.add_argument('-d', '--distance',
                   default='euclid', choices=['euclid', 'cosine'],
                   help='the distance measurement to use')
    p.add_argument('fields', metavar='fields', nargs='+',
                   help='the value columns')
    return p

if __name__ == '__main__':
    parser = buildArgParser()
    args = parser.parse_args()
    KMeans.run(args)
