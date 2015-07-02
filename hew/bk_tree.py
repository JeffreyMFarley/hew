import hew

class BKNode(dict):
    ''' Implementation of a Burkhard-Keller Tree
    Adapted from https://gist.github.com/Arachnid/491973
    '''
    def __init__(self, term):
        self.__dict__ = self
        self.term = term
        self.children = {}
      
    def insert(self, other):
        distance = hew.levenshtein(self.term, other)
        if distance in self.children:
            self.children[distance].insert(other)
        else:
            self.children[distance] = BKNode(other)
  
    def search(self, term, k, results=None):
        if results is None:
            results = []
        distance = hew.levenshtein(self.term, term)
        counter = 1
        if distance <= k:
            results.append(self.term)
        for i in range(max(0, distance - k), distance + k + 1):
            child = self.children.get(i)
            if child:
                counter += child.search(term, k, results)
        return counter

