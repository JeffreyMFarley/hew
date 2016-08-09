class Node(object):
    def __init__(self, data):
        self.data = data
        self.children = []

    def add(self, obj):
        self.children.append(obj)
