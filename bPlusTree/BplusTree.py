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

        # 递归插入，从根结点递归嵌套进入叶结点完成插入，插入之后再做处理（逐步向上）使结点数目合法
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
                    result.extend(leaf1.keyValueList[index1:index2 + 1])
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
            leftChild = node.pointerList[index]
            rightChild = node.pointerList[index + 1]
            if leftChild.isLeaf():
                # 如果合并的是叶结点，将右儿子值复制到左儿子
                leftChild.keyValueList = leftChild.keyValueList \
                                         + rightChild.keyValueList
                leftChild.brother = rightChild.brother
            else:
                # 如果合并的是内结点，将右儿子索引值和node结点index索引值复制到左儿子
                leftChild.indexValueList = \
                    leftChild.indexValueList + [node.indexValueList[index]] \
                    + rightChild.indexValueList
                # 将右儿子结点复制到左儿子
                leftChild.pointerList = leftChild.pointerList + rightChild.pointerList
            # 在node结点删除右儿子
            node.pointerList.remove(rightChild)
            # 在node结点删除索引值（已经移入左儿子作为合并后的结点 或者 合并叶结点之后要删除该索引值）
            node.indexValueList.remove(node.indexValueList[index])
            if not node.indexValueList and node.parent is None:
                # 如果node结点索引清空了，删掉该结点，重置根结点
                node.pointerList[0].parent = None
                self.__root = node.pointerList[0]
                del node
                return self.__root
            else:
                return node.parent

        def transfer_leftToRight(node, index):
            leftChild = node.pointerList[index]
            rightChild = node.pointerList[index + 1]
            if not leftChild.isLeaf():
                # 将index的最后一个结点追加到index+1的第一个结点
                rightChild.pointerList. \
                    insert(0, leftChild.pointerList[-1])
                leftChild.pointerList[-1].parent = \
                    rightChild
                # 追加index+1的索引值
                rightChild.indexValueList \
                    .insert(0, leftChild.indexValueList[-1])
                # 更新node的index+1的索引值
                node.indexValueList[index + 1] = \
                    leftChild.indexValueList[-1]
                # 删除index的最后一个结点和索引值
                leftChild.pointerList.pop()
                leftChild.indexValueList.pop()
            else:
                # 将index的最后一个结点追加到index+1的第一个结点
                rightChild.keyValueList. \
                    insert(0, leftChild.keyValueList[-1])
                # 删除index最后一个结点
                leftChild.keyValueList.pop()
                # 更新node的index索引值
                node.indexValueList[index] = rightChild. \
                    keyValueList[0].key

        def transfer_rightToLeft(node, index):
            leftChild = node.pointerList[index]
            rightChild = node.pointerList[index + 1]
            if not leftChild.isLeaf():
                # 将index+1的第一个结点追加到index的末尾
                leftChild.pointerList. \
                    append(rightChild.pointerList[0])
                rightChild.pointerList[0].parent = \
                    leftChild
                # 追加index的index索引值
                leftChild.indexValueList. \
                    append(rightChild.indexValueList[0])
                # 更新node的index索引值
                node.indexValueList[index] = \
                    rightChild.indexValueList[0]
                # 删除index+1的第一个结点和索引值
                rightChild.pointerList. \
                    remove(rightChild.pointerList[0])
                rightChild.indexValueList. \
                    remove(rightChild.indexValueList[0])
            else:
                # 将index+1的第一个结点追加到index的末尾
                leftChild.keyValueList. \
                    append(rightChild.keyValueList[0])
                # 删除index+1的第一个结点
                rightChild.keyValueList. \
                    remove(rightChild.keyValueList[0])
                # 更新node的index索引值
                node.indexValueList[index] = rightChild. \
                    keyValueList[0].key

        # 递归删除
        def delete_node(node, canDelete=True):
            if node.isLeaf():
                if canDelete:
                    # 找到叶结点，删除对应的键值对（如果存在）
                    sortedList = [x.key for x in node.keyValueList]
                    index = binary_search_left(sortedList, key)
                    try:
                        keyValue = node.keyValueList[index]
                    except IndexError:
                        raise IndexError('index error')
                    else:
                        if keyValue.key != key:
                            raise ValueError('this key does not exist')
                        else:
                            node.keyValueList.remove(keyValue)
                if node.isLessThanHalf():
                    delete_node(node.parent, False)
                if node.parent is not None:
                    parent_indexList = node.parent.indexValueList
                    if key in parent_indexList:
                        i = parent_indexList.index(key)
                        parent_indexList[i] = node.keyValueList[0].key
                return

            else:
                index = binary_search_right(node.indexValueList, key)
                if index == len(node.indexValueList):
                    leftChild = node.pointerList[index - 1]
                    rightChild = node.pointerList[index]
                    if rightChild.isLessThanHalf():
                        if rightChild.isLeaf():
                            if len(rightChild.keyValueList) + len(leftChild.keyValueList) <= self.__order - 1:
                                delete_node(merge(node, index - 1), canDelete)
                            else:
                                transfer_leftToRight(node, index - 1)
                                delete_node(rightChild, canDelete)
                        else:
                            if len(rightChild.pointerList) + len(leftChild.pointerList) <= self.__order:
                                delete_node(merge(node, index - 1), canDelete)
                            else:
                                transfer_leftToRight(node, index - 1)
                                delete_node(rightChild, canDelete)
                    else:
                        delete_node(rightChild, canDelete)
                else:
                    leftChild = node.pointerList[index]
                    rightChild = node.pointerList[index + 1]
                    if leftChild.isLessThanHalf():
                        if leftChild.isLeaf():
                            if len(rightChild.keyValueList) + len(leftChild.keyValueList) <= self.__order - 1:
                                delete_node(merge(node, index), canDelete)
                            else:
                                transfer_rightToLeft(node, index)
                                delete_node(leftChild, canDelete)
                        else:
                            if len(rightChild.pointerList) + len(leftChild.pointerList) <= self.__order:
                                delete_node(merge(node, index), canDelete)
                            else:
                                transfer_rightToLeft(node, index)
                                delete_node(leftChild, canDelete)
                    else:
                        delete_node(leftChild, canDelete)

        delete_node(self.__root)


if __name__ == '__main__':
    l1 = read_data('../ex2.csv')
    # l1 = read_data()
    print([x.__str__() for x in l1])
    print('开始建树')
    bpTree = BplusTree(4)
    for kv in l1:
        bpTree.insert(kv)
        print('insert ', kv)
        print(len(bpTree.leaves()))
        bpTree.show()
        print([str(x.key) + x.value for x in bpTree.leaves()])
        print()
    print('search: ')
    searchResult = bpTree.search(1, 3)
    print([str(x.key) + x.value for x in searchResult])
    print('delete: ')
    bpTree.delete(11)
    bpTree.show()
    bpTree.delete(7)
    bpTree.show()
    print('hello')
    l0 = [3, 5, 6, 7, 8]
    print(l0.index(7))
    print(binary_search_right(l0, 4))
    print(binary_search_left(l0, 4))
    print(l0[-1])
