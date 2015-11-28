import sys
import numpy as np
import random
from hew.structures.math import Vector

if sys.version >= '3':
    xrange = range

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
    def fromTable(cls, k, arrayOfDictionaries, vectorFields, labelFields=[]):
        """ Initializes a k-means instance from a tabular structure """
        for o in arrayOfDictionaries:
            vectors = [float(o[f]) if f in o else 0. for f in vectorFields]
            labels = [o[f] if f in o else '' for f in labelFields]

        return KMeans(k, vectors, labels)

    # -------------------------------------------------------------------------
    # Customization Methods
    # -------------------------------------------------------------------------
    def __init__(self, k, vectors, labels=None):
        assert len(vectors) > 0
        if labels:
            assert len(vectors) == len(labels)

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
        self.labels = labels
        self.k = k
        self.d = len(vectors[0])
        self.MU, self.clusterIndex, self.iter = lloyds_algorithm(vectors, k)

    def __len__(self):
        return len(self.clusterIndex)

    def __iter__(self):
        for c in self.clusterIndex:
            yield c

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    pass
