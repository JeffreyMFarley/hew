try:
    from itertools import izip
except ImportError:  # python3.x
    izip = zip


# -----------------------------------------------------------------------------

def extractFloatVectors(arrayOfDictionaries, vectorFields):
    """ Return the numeric fields from a dataset """
    vectors = []
    for o in arrayOfDictionaries:
        vectors.append(tuple([float(o[f])
                              if f in o else 0.
                              for f in vectorFields]))
    return vectors

# -----------------------------------------------------------------------------


def bounds(vectors):
    """ Determines the minimum and maximum values from an array of vectors"""
    d = len(vectors[0])
    mins = [float("inf")] * d
    maxs = [-float("inf")] * d
    for x in vectors:
        for i, v in enumerate(x):
            if v < mins[i]:
                mins[i] = v
            if v > maxs[i]:
                maxs[i] = v

    return mins, maxs


def centroid(vectors):
    """ Centroid of the vectors """
    d = len(vectors[0])
    c = [0.] * d
    n = len(vectors)
    for x in vectors:
        for i, v in enumerate(x):
            c[i] += v
    for i in range(d):
        c[i] /= n
    return c


def distance_cosine_similarity(a, b):
    """ Calculates the Ochini coefficient between two vectors"""
    from math import acos

    numerator = dot(a, b)
    denominator = length(a) * length(b)
    x = numerator/denominator if denominator else 0
    bounded_x = min(1, max(x, -1))
    return acos(bounded_x)


def distance_euclid_squared(a, b):
    """ Calculates the Euclidean distance between two vectors"""
    s = 0
    for x, y in izip(a, b):
        d = x - y
        s += d * d
    return s


def distance_manhattan(a, b):
    """ Calculates the Manhattan distance between two vectors"""
    from math import fabs

    s = 0
    for x, y in izip(a, b):
        s += fabs(x - y)
    return s


def dot(a, b):
    """ Calculates the dot product of two vectors"""
    s = 0
    for x, y in izip(a, b):
        s += x * y
    return s


def length(a):
    """ Calculates the length of a vector"""
    from math import sqrt

    s = 0
    for x in a:
        s += x * x
    return sqrt(s)
