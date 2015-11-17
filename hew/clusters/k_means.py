import sys
import numpy as np
import random
import collections
from hew.structures.kd_tree import square_distance as dist

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

def random_point(d=2):
    return tuple([random.uniform(-1, 1) for _ in range(d)])

# -----------------------------------------------------------------------------
# () -> X
# -----------------------------------------------------------------------------

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

# -----------------------------------------------------------------------------
# X -> ...
# -----------------------------------------------------------------------------

def mean(X):
    """ Centroid of the vectors """
    d = len(X[0])
    c = [0.] * d
    n = len(X)
    for x in X:
        for i, v in enumerate(x):
            c[i] += v
    for i in xrange(d):
        c[i] /= n
    return c

def bounding_box(X):
    xmin, xmax = min(X,key=lambda a:a[0])[0], max(X,key=lambda a:a[0])[0]
    ymin, ymax = min(X,key=lambda a:a[1])[1], max(X,key=lambda a:a[1])[1]
    return (xmin,xmax), (ymin,ymax)
 
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

def cluster_points(X, mu):
    clusters  = {}
    for x in X:
        bestmukey = min([
                         (i[0], np.linalg.norm(x-mu[i[0]]))
                         for i in enumerate(mu)
                        ], 
                        key=lambda t:t[1])[0]
        try:
            clusters[bestmukey].append(x)
        except KeyError:
            clusters[bestmukey] = [x]
    return clusters
 
# -----------------------------------------------------------------------------
# mu -> ...
# -----------------------------------------------------------------------------

def has_converged(A, B):
    return set([tuple(a) for a in A]) == set([tuple(b) for b in B])
 
def reevaluate_centers(mu, clusters):
    newmu = []
    keys = sorted(clusters.keys())
    for k in keys:
        newmu.append(np.mean(clusters[k], axis = 0))
    return newmu
 
def Wk(mu, clusters):
    K = len(mu)
    return sum([np.linalg.norm(mu[i]-c)**2/(2*len(c))
                for i in range(K) 
                for c in clusters[i]])

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def kmeans(X, k):
    # Initialize from random points.
    l = len(X)
    MU = [X[i] for i in random.sample(xrange(l), k)]
    B = [X[i] for i in random.sample(xrange(l), k)]
    clusters = [None] * l

    while not has_converged(MU, B):
        print('.')
        B = list(MU)
        for i, x in enumerate(X):
            clusters[i] = min(xrange(k), key=lambda j: dist(x, MU[j]))
        for j, mu in enumerate(MU):
            members = [x for i, x in enumerate(X) if clusters[i] == j]
            MU[j] = mean(members)

    return MU, clusters

if __name__ == '__main__':
    X = init_board_gauss(2000,6, 6)
    c = kmeans(X, 6)

    print(c)

    #ks, logWks, logWkbs, sk = gap_statistic(X)
    #print(ks, logWks, logWkbs, sk)
