class KeyValue:
    def __init__(self, key, value):
        self.__key = key
        self.__value = value

    def __str__(self):
        return str((self.__key, self.__value))
