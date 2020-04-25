class InterNode:
    def __init__(self, order):
        self.__order = order
        self.indexValueList = []  # 索引值
        self.pointerList = []  # 指向某一个结点的指针
        self.parent = None

    @staticmethod
    def isLeaf():
        return False

    def isFull(self):
        return len(self.indexValueList) > self.__order - 1

    def isLessThanHalf(self):
        return len(self.indexValueList) < (self.__order - 1) / 2 - 1
