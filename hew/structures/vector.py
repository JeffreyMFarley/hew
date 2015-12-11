try:
    from itertools import izip
except ImportError:  #python3.x
    izip = zip

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

def distance_euclid_squared(a, b):
    s = 0
    for x, y in izip(a, b):
        d = x - y
        s += d * d
    return s
