import os
import sys
import csv
#import numpy as np
import random
import argparse
from hew.structures.math import Vector, MonteCarlo

try:
    from itertools import izip
except ImportError:  #python3.x
    izip = zip

if sys.version >= '3':
    xrange = range

# -----------------------------------------------------------------------------
# obj -> obj
# -----------------------------------------------------------------------------

def convertBooleanFields(o):
    for k,v in o.items():
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
# mu :: the center point of a cluster
# MU :: array of center points
# X  :: a set of n points
# x  :: a point vector
# k  :: number of clusters
# d  :: number of dimensions

# -----------------------------------------------------------------------------
# Optimal cluster
# -----------------------------------------------------------------------------

# https://datasciencelab.wordpress.com/2013/12/27/finding-the-k-in-k-means-clustering/
def optimal_clusters(vectors, max_k=10, samples=10):
    """ `vectors` is the input array of points to test
    `max_k` is the maximum number of clusters to test for
    `samples` is the number of monte carlo simulations to run at each cluster step
    """
    from hew.structures.math import RunningStatistics
    import math

    mins, maxs = Vector.bounds(vectors)
    B_Generator = MonteCarlo(mins, maxs)
    nX = len(vectors)

    Gap = [0.] * (max_k + 1)
    SSD = [0.] * (max_k + 1)
    WK0 = [0.] * (max_k + 1)
    WKB = [0.] * (max_k + 1)

    print('Checking for optimal cluster size', file=sys.stderr)

    for k in range(1, max_k + 1):
        c = KMeans(k, vectors)
        print('  ', k, file=sys.stderr)

        s = RunningStatistics()
        for _ in range(samples):
            B = list(B_Generator.xrange(nX))
            b = KMeans(k, B)
            s += math.log(b.Wk)

        WK0[k] = math.log(c.Wk)
        WKB[k] = s.mean
        SSD[k] = s.standard_deviation * math.sqrt(1 + 1/s.count)
        Gap[k] = s.mean - WK0[k]

    opt_k = None
    for k in range(1, max_k - 1):
        next = Gap[k+1] - SSD[k+1]
        delta = Gap[k] - next
        if delta > 0 and not opt_k:
            opt_k = k
        #print(k, WK0[k], WKB[k], Gap[k], next, delta)
    
    return opt_k

# -----------------------------------------------------------------------------

def has_converged(A, B):
    return set([tuple(a) for a in A]) == set([tuple(b) for b in B])
 
class KMeans:
    # -------------------------------------------------------------------------
    # Factory Methods
    # -------------------------------------------------------------------------
    @classmethod
    def fromTable(cls, k, arrayOfDictionaries, vectorFields):
        """ Initializes a k-means instance from a tabular structure """
        vectors = []
        for o in arrayOfDictionaries:
            vectors.append(tuple([float(o[f]) 
                                  if f in o else 0. 
                                  for f in vectorFields]))

        if k == -1:
            k = optimal_clusters(vectors)

        return KMeans(k, vectors)

    # -------------------------------------------------------------------------
    # Customization Methods
    # -------------------------------------------------------------------------
    def __init__(self, k, vectors):
        assert len(vectors) > 0

        def lloyds_algorithm(X, k):
            # Initialize from random points.
            l = len(X)
            MU = random.sample(set(X), k)
            C = [None] * l
            iterations = 0
            done = False

            while not done:
                old = list(MU)
                iterations += 1

                for i, x in enumerate(X):
                    C[i] = min(xrange(k), 
                               key=lambda j: Vector.square_distance(x, MU[j]))
                for j, mu in enumerate(MU):
                    members = [x for i, x in enumerate(X) if C[i] == j]
                    MU[j] = Vector.mean(members)

                done = has_converged(MU, old)

            return MU, C, iterations

        self.vectors = vectors
        self.k = k
        self.d = len(vectors[0])
        self.MU, self.clusterIndex, self.iter = lloyds_algorithm(vectors, k)
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
        coeff = [1/(2*len(C[i])) for i in xrange(self.k)]

        return sum([Vector.square_distance(self.MU[i], c) # * coeff[i]
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
            input = [convertBooleanFields(row) for row in reader]

        k_means = KMeans.fromTable(args.clusters, input, args.fields)

        with open(args.outputFileName, 'w') as f:
            cells = list(out_cols)
            cells.append(args.resultColumn)
            print('\t'.join(cells), file=f)

            for orig, cluster in izip(input, k_means):
                cells = [str(orig[x]) for x in out_cols]
                cells.append(str(cluster + 1))
                print('\t'.join(cells), file=f)

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def buildArgParser():
    description = 'Determine clusters from a table of features'
    p = argparse.ArgumentParser(description=description)
    p.add_argument('input', metavar='inputFileName',
                   help='the file to process')
    p.add_argument('-c', '--clusters', metavar='clusters',
                   default=-1,
                   help='the number of clusters')
    p.add_argument('-r', '--results', metavar='resultColumn',
                   default='cluster',
                   help='the column that holds the result')
    p.add_argument('-o', '--output', metavar='outputFileName',
                   default='clusters.txt',
                   help='the name of the file that will hold the results')
    p.add_argument('fields', metavar='fields', nargs='+',
                   help='the value columns')
    return p

if __name__ == '__main__':
    parser = buildArgParser()
    args = parser.parse_args()
    KMeans.run(args)
