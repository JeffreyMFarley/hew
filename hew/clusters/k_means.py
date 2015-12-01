import os
import sys
import csv
#import numpy as np
import random
import argparse
from hew.structures.math import Vector

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
# Use later... find optimal cluster Number
# -----------------------------------------------------------------------------

def gap_statistic(X):
    (xmin,xmax), (ymin,ymax) = bounding_box(X)
    # Dispersion for real distribution
    ks = range(1,10)
    Wks = np.zeros(len(ks))
    Wkbs = np.zeros(len(ks))
    sk = np.zeros(len(ks))
    for indk, k in enumerate(ks):
        mu, clusters = find_centers(X,k)
        Wks[indk] = np.log(Wk(mu, clusters))
        # Create B reference datasets
        B = 10
        BWkbs = np.zeros(B)
        for i in range(B):
            Xb = []
            for n in range(len(X)):
                Xb.append([random.uniform(xmin,xmax),
                          random.uniform(ymin,ymax)])
            Xb = np.array(Xb)
            mu, clusters = find_centers(Xb,k)
            BWkbs[i] = np.log(Wk(mu, clusters))
        Wkbs[indk] = sum(BWkbs)/B
        sk[indk] = np.sqrt(sum((BWkbs-Wkbs[indk])**2)/B)
    sk = sk*np.sqrt(1+1/B)
    return(ks, Wks, Wkbs, sk)

def Wk(mu, clusters):
    K = len(mu)
    return sum([np.linalg.norm(mu[i]-c)**2/(2*len(c))
                for i in range(K) 
                for c in clusters[i]])

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

    def __len__(self):
        return len(self.clusterIndex)

    def __iter__(self):
        for c in self.clusterIndex:
            yield c

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
                   default=6,
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
