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
# mu :: the center point of a centroid
# X  :: a set of N points
# K  :: number of clusters

def random_point(axes=2):
    return tuple([random.uniform(-1, 1) for _ in range(axes)])

# -----------------------------------------------------------------------------
# () -> X
# -----------------------------------------------------------------------------

def init_board(N, axes=2):
    return [random_point(axes) for i in range(N)]

def init_board_gauss(N, k, axes=2):
    n = N // k
    X = []
    for i in range(k):
        c = random_point(axes)
        s = random.uniform(0.05,0.33)
        for _ in range(n):
            point = tuple([random.gauss(c[axis],s) for axis in range(axes)])
            X.append(point)
    return X

# -----------------------------------------------------------------------------
# X -> ...
# -----------------------------------------------------------------------------

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
 
def find_centers(X, K):
    # Initialize to K random centers
    oldmu = random.sample(X, K)
    mu = random.sample(X, K)
    while not has_converged(mu, oldmu):
        oldmu = mu
        # Assign all points in X to clusters
        clusters = cluster_points(X, mu)
        # Reevaluate centers
        mu = reevaluate_centers(oldmu, clusters)
    return(mu, clusters)

# -----------------------------------------------------------------------------
# mu -> ...
# -----------------------------------------------------------------------------

def has_converged(mu_1, mu_0):
    return set([tuple(a) for a in mu_1]) == set([tuple(a) for a in mu_0])
 
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

def mean(xs):
    """Mean (as a dense vector) of a set of sparse vectors of length l."""
    l = len(xs)
    c = [0.] * l
    n = 0
    for x in xs:
        for i, v in x:
            c[i] += v
        n += 1
    for i in xrange(l):
        c[i] /= n
    return c

def kmeans(k, X, n_iter=10):
    # Initialize from random points.
    l = len(X)
    centers = [X[i] for i in random.sample(xrange(l), k)]
    cluster = [None] * l

    for _ in xrange(n_iter):
        for i, x in enumerate(X):
            cluster[i] = min(xrange(k), key=lambda j: dist(x, centers[j]))
        for j, c in enumerate(centers):
            members = (x for i, x in enumerate(X) if cluster[i] == j)
            centers[j] = mean(members, l)

    return cluster

if __name__ == '__main__':
    X = init_board_gauss(200,3, 6)
    c = kmeans(3, X)

    #ks, logWks, logWkbs, sk = gap_statistic(X)
    #print(ks, logWks, logWkbs, sk)
