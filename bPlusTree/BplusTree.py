from collections import deque

import pandas as pd

from bPlusTree.InterNode import InterNode
from bPlusTree.KeyValue import KeyValue
from bPlusTree.LeafNode import LeafNode


def read_data(filename='../data.csv'):
    keyValueList = []
    data = pd.read_csv(filename, sep=',')
    for number, keyValue in data.iterrows():
        key = keyValue["key"]
        value = keyValue["value"]
        keyValueList.append(KeyValue(key, value))
    return keyValueList


def binary_search_right(sortedList, element, low=0, high=None):
    if low < 0:
        raise ValueError('low can not be negative')
    if high is None:
        high = len(sortedList)
    while low < high:
        mid = (low + high) // 2
        if element < sortedList[mid]:
            high = mid
        else:
            low = mid + 1
    return low


def binary_search_left(sortedList, element, low=0, high=None):
    if low < 0:
        raise ValueError('low can not be negative')
    if high is None:
        high = len(sortedList)
    while low < high:
        mid = (low + high) // 2
        if element > sortedList[mid]:
            low = mid + 1
        else:
            high = mid
    return low


class BplusTree:
    def __init__(self, order):
        self.__order = order
        self.__root = LeafNode(order)
        self.__leaf = self.__root

    def insert(self, keyValue):
        node = self.__root

        def split_inter(interNode):
            newNode = InterNode(self.__order)
            mid = self.__order // 2 + 1
            newNode.indexValueList = interNode.indexValueList[mid:]
            newNode.pointerList = interNode.pointerList[mid:]
            newNode.parent = interNode.parent
            for pointer in newNode.pointerList:
                pointer.parent = newNode
            if interNode.parent is None:
                newRoot = InterNode(self.__order)
                newRoot.indexValueList = [interNode.indexValueList[mid - 1]]
                newRoot.pointerList = [interNode, newNode]
                interNode.parent = newRoot
                newNode.parent = newRoot
                self.__root = newRoot
            else:
                parent = interNode.parent
                index = parent.pointerList.index(interNode)
                parent.indexValueList.insert(index, interNode.indexValueList[mid - 1])
                parent.pointerList.insert(index + 1, newNode)
            interNode.indexValueList = interNode.indexValueList[:mid - 1]
            interNode.pointerList = interNode.pointerList[:mid]
            return interNode.parent

        def split_leaf(leafNode):
            mid = self.__order // 2
            newLeaf = LeafNode(self.__order)
            newLeaf.keyValueList = leafNode.keyValueList[mid:]
            if leafNode.parent is None:
                newRoot = InterNode(self.__order)
                newRoot.indexValueList = [leafNode.keyValueList[mid].key]
                newRoot.pointerList = [leafNode, newLeaf]
                leafNode.parent = newRoot
                newLeaf.parent = newRoot
                self.__root = newRoot
            else:
                parent = leafNode.parent
                index = parent.pointerList.index(leafNode)
                parent.indexValueList.insert(index, leafNode.keyValueList[mid].key)
                parent.pointerList.insert(index + 1, newLeaf)
                newLeaf.parent = leafNode.parent
            leafNode.keyValueList = leafNode.keyValueList[:mid]
            leafNode.brother = newLeaf
            return leafNode.parent

        def insert_node(n, canInsert=True):
            if n.isLeaf():
                if canInsert:
                    sortedList = [x.key for x in n.keyValueList]
                    index = binary_search_right(sortedList, keyValue.key)
                    n.keyValueList.insert(index, keyValue)
                if n.isFull():
                    insert_node(split_leaf(n), False)
                else:
                    return
            else:
                if n.isFull():
                    insert_node(split_inter(n), canInsert)
                else:
                    index = binary_search_right(n.indexValueList, keyValue.key)
                    insert_node(n.pointerList[index], canInsert)

        insert_node(node)

    def show(self):
        print('B+ Tree: ')
        queue = deque()
        height = 0
        queue.append([self.__root, height])
        while True:
            try:
                w, h = queue.popleft()
            except IndexError:
                return
            else:
                if not w.isLeaf():
                    print(w.indexValueList, 'inter height = ', h)
                    if h == height:
                        height += 1
                    queue.extend([[i, height] for i in w.pointerList])
                else:
                    print([v.key for v in w.keyValueList], 'leaf height =', h)

    def search(self):
        pass

    def delete(self):
        pass


if __name__ == '__main__':
    l1 = read_data('../ex2.csv')
    # l1 = read_data()
    print([x.__str__() for x in l1])
    bpTree = BplusTree(4)
    for kv in l1:
        bpTree.insert(kv)
        print('insert ', kv)
        bpTree.show()
        print()

    print('hello')
