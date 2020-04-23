class InterNode:
    def __init__(self, n):
        self.__n = n
        self.__indexValueList = []  # 索引值
        self.__pointerList = []  # 指向某一个结点的指针

    def isFull(self):
        return len(self.__pointerList) == self.__n

    def isLessThanHalf(self):
        return len(self.__pointerList) < self.__n / 2
