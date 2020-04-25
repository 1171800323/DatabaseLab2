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
            newLeaf.brother = leafNode.brother
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

    def leaves(self):
        result = []
        leaf = self.__leaf
        while True:
            result.extend(leaf.keyValueList)
            if leaf.brother is None:
                return result
            else:
                leaf = leaf.brother
        return result

    def search(self, low=None, high=None):
        result = []
        node = self.__root
        leaf = self.__leaf
        if low is None and high is None:
            raise ValueError('no range')
        elif low is not None and high is not None and low > high:
            raise ValueError('lower can not be greater than upper')

        def search_key(n, k):
            if n.isLeaf():
                sortedList = [x.key for x in n.keyValueList]
                i = binary_search_left(sortedList, k)
                return i, n
            else:
                i = binary_search_right(n.indexValueList, k)
                return search_key(n.pointerList[i], k)

        if low is None:
            while True:
                for keyValue in leaf.keyValueList:
                    if keyValue.key <= high:
                        result.append(keyValue)
                    else:
                        return result
                    if leaf.brother is None:
                        return result
                    else:
                        leaf = leaf.brother
        elif high is None:
            index, leaf = search_key(node, low)
            result.extend(leaf.keyValueList[index:])
            while True:
                if leaf.brother is None:
                    return result
                else:
                    leaf = leaf.brother
                    result.extend(leaf.keyValueList)
        else:
            if low == high:
                index, leaf = search_key(node, low)
                try:
                    if leaf.keyValueList[index].key == low:
                        result.append(leaf.keyValueList[index])
                        return result
                    else:
                        return result
                except IndexError:
                    return result
            else:
                index1, leaf1 = search_key(node, low)
                index2, leaf2 = search_key(node, high)
                if leaf1 is leaf2:
                    result.extend(leaf1.keyValueList[index1:index2])
                    return result
                else:
                    result.extend(leaf1.keyValueList[index1:])
                    leaf = leaf1
                    while True:
                        if leaf.brother is leaf2:
                            result.extend(leaf2.keyValueList[:index2 + 1])
                            return result
                        else:
                            result.extend(leaf.brother.keyValueList)
                            leaf = leaf.brother

    def delete(self, key):
        def merge(node, index):
            child = node.pointerList[index]
            if child.isLeaf():
                child.keyValueList = child.keyValueList \
                                     + node.pointerList[index + 1].keyValueList
                child.brother = node.pointerList[index + 1].brother
            else:
                child.indexValueList = \
                    child.indexValueList + [node.indexValueList[index]] \
                    + node.pointerList[index + 1].indexValueList
                child.pointerList = child.pointerList \
                                    + node.pointerList[index + 1].pointerList
            node.poiterList.remove(node.pointerList[index + 1])
            node.indexValueList.remove(node.indexValueList[index])
            if not node.indexValueList:
                node.pointerList[0].parent = None
                self.__root = node.pointerList[0]
                del node
                return self.__root
            else:
                return node

        def transfer_leftToRight(node, index):
            if not node.pointerList[index].isLeaf():
                node.pointerList[index + 1].pointerList. \
                    insert(0, node.pointerList[index].pointerList[-1])
                node.pointerList[index].pointerList[-1].parent = \
                    node.pointerList[index + 1]
                node.pointerList[index + 1].indexValueList \
                    .insert(0, node.pointerList[index].indexValueList[-1])
                node.indexValueList[index + 1] = \
                    node.pointerList[index].indexValueList[-1]
                node.pointerList[index].pointerList.pop()
                node.pointerList[index].indexValueList.pop()
            else:
                node.pointerList[index + 1].keyValueList. \
                    insert(0, node.pointerList[index].keyValueList[-1])
                node.pointerList[index].keyValueList.pop()
                node.indexValueList[index] = node.pointerList[index + 1]. \
                    keyValueList[0].key

        def transfer_rightToLeft(node, index):
            if not node.pointerList[index].isLeaf():
                node.pointerList[index].pointerList. \
                    append(node.pointerList[index + 1].pointerList[0])
                node.pointerList[index + 1].pointerList[0].parent = \
                    node.pointerList[index]
                node.pointerList[index].indexValueList. \
                    append(node.pointerList[index + 1].indexValueList[0])
                node.indexValueList[index] = \
                    node.pointerList[index + 1].indexValueList[0]
                node.pointerList[index + 1].pointerList. \
                    remove(node.pointerList[index + 1].pointerList[0])
                node.pointerList[index + 1].indexValueList. \
                    remove(node.pointerList[index + 1].indexValueList[0])
            else:
                node.pointerList[index].keyValueList. \
                    append(node.pointerList[index + 1].keyValueList[0])
                node.pointerList[index + 1].keyValueList. \
                    remove(node.pointerList[index + 1].keyValueList[0])
                node.indexValueList[index] = node.pointerList[index + 1]. \
                    keyValueList[0].key

        def delete_node(node, k):
            if not node.isLeaf():
                index = binary_search_right(node.indexValueList, k)
                if index == len(node.indexValueList):
                    if not node.pointerList[index].isLessThanHalf():
                        return delete_node(node.pointerList[index], k)
                    elif not node.pointerList[index - 1].isLessThanHalf():
                        transfer_leftToRight(node, index - 1)
                        return delete_node(node.pointerList[index], k)
                    else:
                        return delete_node(merge(node, index - 1), k)
                else:
                    if not node.pointerList[index].isLessThanHalf():
                        return delete_node(node.pointerList[index], k)
                    elif not node.pointerList[index + 1].isLessThanHalf():
                        transfer_rightToLeft(node, index)
                        return delete_node(node.pointerList[index], k)
                    else:
                        return delete_node(merge(node, index), k)
            else:
                sortedList = [x.key for x in node.keyValueList]
                index = binary_search_left(sortedList, k)
                try:
                    keyValue = node.keyValueList[index]
                except IndexError:
                    return -1
                else:
                    if keyValue.key != k:
                        return -1
                    else:
                        node.keyValueList.remove(keyValue)
                        return 0

        delete_node(self.__root, key)


if __name__ == '__main__':
    l1 = read_data('../ex2.csv')
    # l1 = read_data()
    print([x.__str__() for x in l1])
    bpTree = BplusTree(4)
    for kv in l1:
        bpTree.insert(kv)
        print('insert ', kv)
        bpTree.show()
        print([x.key for x in bpTree.leaves()])
        print()

    print('hello')
    l0 = [3, 5]
    print(binary_search_right(l0, 6))
    print(binary_search_left(l0, 5))
    print(l0[-1])
