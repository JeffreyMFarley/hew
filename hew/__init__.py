# Provide the public interface to the module

from hew.normalizer import Normalizer
from hew.classifiers.c45 import C45
from hew.clusters.k_means import KMeans
from hew.structures.bk_tree import BKNode
from hew.structures.kd_tree import KDTree
from hew.structures.vector import distance_euclid_squared as distance_fn
