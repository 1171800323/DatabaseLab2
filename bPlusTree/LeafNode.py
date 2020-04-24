class LeafNode:
    def __init__(self, order):
        self.__order = order
        self.keyValue = []
        self.brother = None
        self.parent = None

    @staticmethod
    def isLeaf():
        return True

    def isFull(self):
        return len(self.keyValue) >= self.__order - 1

    def isLessThanHalf(self):
        return len(self.keyValue) < (self.__order - 1) / 2
