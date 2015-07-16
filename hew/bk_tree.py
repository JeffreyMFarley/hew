import hew
import distance

class BKNode(dict):
    ''' Implementation of a Burkhard-Keller Tree
    Adapted from https://gist.github.com/Arachnid/491973
    '''
    def __init__(self, term):
        self.__dict__ = self
        self.term = term
        self.children = {}
      
    def insert(self, other):
        d = distance.levenshtein(self.term, other)
        if d in self.children:
            self.children[d].insert(other)
        else:
            self.children[d] = BKNode(other)
  
    def search(self, term, k, results=None):
        if results is None:
            results = []
        d = distance.levenshtein(self.term, term)
        counter = 1
        if d <= k:
            results.append(self.term)
        for i in range(max(0, d - k), d + k + 1):
            child = self.children.get(i)
            if child:
                counter += child.search(term, k, results)
        return counter

