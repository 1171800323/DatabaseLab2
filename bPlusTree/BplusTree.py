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


# 二分查找，返回的位置及其之后的元素都是大于element的
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


# 二分查找， 返回的位置之前的都是小于element的
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
        node = self.__root  # 从根结点开始向下搜索找到对应的叶结点

        # 分裂内结点，伴随一个索引值上升到父结点（若无父结点则创建），最后返回父结点
        def split_inter(interNode):
            # 创建新结点，复制分裂结点的后半截，注意下方mid-1位置元素要上升到父结点，故不添加到新结点
            newNode = InterNode(self.__order)
            mid = self.__order // 2 + 1
            newNode.indexValueList = interNode.indexValueList[mid:]
            newNode.pointerList = interNode.pointerList[mid:]
            # 设置新节点父亲
            newNode.parent = interNode.parent
            # 为新节点子女重置父亲
            for pointer in newNode.pointerList:
                pointer.parent = newNode
            # 如果没有父亲则创建，并将该父亲设为根结点，子女为分裂出来的这两个节点
            if interNode.parent is None:
                newRoot = InterNode(self.__order)
                newRoot.indexValueList = [interNode.indexValueList[mid - 1]]
                newRoot.pointerList = [interNode, newNode]
                interNode.parent = newRoot
                newNode.parent = newRoot
                self.__root = newRoot
            else:
                # 如果已有，则将mid-1位置元素上升到父节点
                # 此处暂不监测父节点是否合法，待具体插入时做处理
                parent = interNode.parent
                index = parent.pointerList.index(interNode)
                parent.indexValueList.insert(index, interNode.indexValueList[mid - 1])
                parent.pointerList.insert(index + 1, newNode)
            # 分裂后的结点只剩下前半截
            interNode.indexValueList = interNode.indexValueList[:mid - 1]
            interNode.pointerList = interNode.pointerList[:mid]
            return interNode.parent

        # 分裂叶结点，分裂后的两个叶结点的最小索引值为p小的，q大的，将q的副本插入到父结点中（若无则创建）
        # 最后返回父结点
        def split_leaf(leafNode):
            # 创建新叶节点
            mid = self.__order // 2
            newLeaf = LeafNode(self.__order)
            newLeaf.keyValueList = leafNode.keyValueList[mid:]
            # 如果还没有父亲，则新建内结点作为父亲，并成为树根
            if leafNode.parent is None:
                newRoot = InterNode(self.__order)
                newRoot.indexValueList = [leafNode.keyValueList[mid].key]
                newRoot.pointerList = [leafNode, newLeaf]
                leafNode.parent = newRoot
                newLeaf.parent = newRoot
                self.__root = newRoot
            else:
                # 如果已有，将新建结点的最小值副本插入父亲
                # 此处父亲结点可能会满需要分裂，但此处不做处理，留待具体插入时进行
                parent = leafNode.parent
                index = parent.pointerList.index(leafNode)
                parent.indexValueList.insert(index, leafNode.keyValueList[mid].key)
                parent.pointerList.insert(index + 1, newLeaf)
                newLeaf.parent = leafNode.parent
            # 设置分裂结点元素
            leafNode.keyValueList = leafNode.keyValueList[:mid]
            # 设置叶结点之间指针
            newLeaf.brother = leafNode.brother
            leafNode.brother = newLeaf
            return leafNode.parent

        # 递归插入，从根结点递归嵌套进入叶结点完成插入，插入之后再做处理使结点数目合法
        def insert_node(n, canInsert=True):
            if n.isLeaf():
                # 如果是叶结点，找到合适的位置完成插入
                if canInsert:
                    sortedList = [x.key for x in n.keyValueList]
                    index = binary_search_right(sortedList, keyValue.key)
                    n.keyValueList.insert(index, keyValue)
                # 如果叶结点满了，分裂叶结点，并再次从父结点开始插入（假插入，为的是解决父节点可能会满的问题）
                if n.isFull():
                    insert_node(split_leaf(n), False)
                else:
                    return
            else:
                # 如果是内结点，满了，就分裂，从其父节点开始插入
                # 如果父节点也满了，分裂并从父节点的父节点开始插入，以此类推，确保所有结点数目合法
                if n.isFull():
                    insert_node(split_inter(n), canInsert)
                else:
                    # 内结点不满，寻找适合插入的子女结点进行插入
                    index = binary_search_right(n.indexValueList, keyValue.key)
                    insert_node(n.pointerList[index], canInsert)

        insert_node(node)

    # 打印整棵树
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

    # 依次输出所有叶结点存储的键值对
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

    # 查询，从根结点开始，逐渐向下进入内结点，最后进入叶结点
    def search(self, low=None, high=None):
        result = []
        node = self.__root
        leaf = self.__leaf
        if low is None and high is None:
            raise ValueError('no range')
        elif low is not None and high is not None and low > high:
            raise ValueError('lower can not be greater than upper')

        # 寻找键值所在叶结点
        def search_key(n, k):
            if n.isLeaf():
                sortedList = [x.key for x in n.keyValueList]
                i = binary_search_left(sortedList, k)
                return i, n
            else:
                i = binary_search_right(n.indexValueList, k)
                return search_key(n.pointerList[i], k)

        if low is None:
            # 寻找所有<=high的键值对，从第一片叶结点出发，沿着brother指针往后寻找，直到键值大于high
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
            # 寻找所有>=low的键值对，先找到存储键值为low或者小于low的结点，从该叶结点往后查找直到最后
            index, leaf = search_key(node, low)
            result.extend(leaf.keyValueList[index:])
            while True:
                if leaf.brother is None:
                    return result
                else:
                    leaf = leaf.brother
                    result.extend(leaf.keyValueList)
        else:
            # 如果low和high相等，先找到存储键值为low或者小于low的结点
            # 如果该结点有和low相等的键值，则返回，否则返回空的list
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
                # 分别找到存储键值low和high的结点，从low所在结点出发往后寻找直到high所在结点
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

    # 根据键值删除
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

        # 递归删除
        def delete_node(node, k):
            if not node.isLeaf():
                # 先对内结点做一些处理，然后再进入叶结点删除
                index = binary_search_right(node.indexValueList, k)
                # 如果结点数目少于一半（精确地说，删除一个会造成该结点数目不合法）
                # 则应该找左右兄弟结点：
                # 1. 兄弟结点能够借给它一个值（借出之后数目合法），然后再删除
                # 2. 合并兄弟结点，然后对合并节点删除
                # 如果不少于一半，即删除一个也不会引起不合法，那就直接进入该结点删除
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
                # 找到叶结点，删除对应的键值对（如果存在）
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
        print([str(x.key)+x.value for x in bpTree.leaves()])
        print()

    print('hello')
    l0 = [3, 5, 6, 7, 8]
    print(binary_search_right(l0, 4))
    print(binary_search_left(l0, 4))
    print(l0[-1])
