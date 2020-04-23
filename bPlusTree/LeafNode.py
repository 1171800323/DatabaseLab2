class LeafNode:
    def __init__(self, n):
        self.__n = n
        self.__keyValue = []
        self.__brother = None
        self.__parent = None

    def setBrother(self, brother):
        self.__brother = brother

    def setParent(self, parent):
        self.__parent = parent

    def getBrother(self):
        return self.__brother

    def getParent(self):
        return self.__parent

    def isFull(self):
        return len(self.__keyValue) == self.__n - 1

    def isLessThanHalf(self):
        return len(self.__keyValue) < (self.__n - 1) / 2
