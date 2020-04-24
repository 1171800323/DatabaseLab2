from bPlusTree.InterNode import InterNode
from bPlusTree.KeyValue import KeyValue
from bPlusTree.LeafNode import LeafNode


class BplusTree:
    def __init__(self, order):
        self.__order = order
        self.__root = LeafNode(order)
        self.__leaf = self.__root

    def insert(self, keyValue):
        node = self.__root

        def split_node(n1):
            newNode = InterNode(self.__order)
            mid = self.__order // 2 + 1
            newNode.indexValueList = n1.indexValueList[mid:]
            newNode.pointerList = n1.pointerList[mid:]
            newNode.parent = n1.parent

        def split_leaf(n2):
            pass

        def insert_node(n):
            pass

        insert_node(node)

    pass


if __name__ == '__main__':
    k1 = KeyValue(1, 'a')
    print(k1)
    a = ['1', '2', '3', '4', '5']
    print(a)
    print(a[len(a) // 2:])
    print(a[2:])
    print(a[:2])
