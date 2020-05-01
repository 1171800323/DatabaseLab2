import os
import sys
from collections import deque

import pandas as pd

# 计划分成4个子集合，每个子集合5块，一块有52428个元素
# 最后一个子集合有一块只有3868个元素
# 内存一次可放5块
# 先对每个子集合内排序，再做4路归并（1块作为输出）

block_size = 52428  # 一块有52428个元素
child_sets_size = 5 * block_size  # 一个子集合有5块（4个子集合）
record_size = 1000000


def handle_child_sets(child_sets, sets_num):
    block = []
    block_num = 1
    size = 0
    for key in sorted(child_sets):
        size += 1
        block.append(key)
        if len(block) == block_size or \
                size == len(child_sets):
            file_name = 'temp/' + str(sets_num) + '-' + str(block_num) + '.txt'
            with open(file_name, 'w', encoding='utf-8') as f:
                for k in block:
                    f.write(str(k) + '\n')
            block.clear()
            block_num += 1


def split(filename='../data.csv', run=False):
    if run:
        child_sets = []
        num = 1
        data = pd.read_csv(filename, sep=',')
        for number, keyValue in data.iterrows():
            key = int(keyValue["key"])
            child_sets.append(key)
            if len(child_sets) == child_sets_size \
                    or number == record_size - 1:
                handle_child_sets(child_sets, num)
                num += 1
                child_sets.clear()


def get_temp_file():
    file_dict = dict()
    for file in os.listdir('temp/'):
        key = int(file[:file.index('-')])
        file_dict.setdefault(key, deque())
        file_dict.get(key).append(file)
    return file_dict


def read_block(filename):
    result = deque()
    filename = 'temp/' + filename
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            result.append(int(line.strip()))
    return result


def write_block(block, filename='result.txt'):
    with open(filename, 'a', encoding='utf-8') as f:
        for key in block:
            f.write(str(key) + '\n')


def merge(run=False):
    if run:
        file_dict = get_temp_file()
        block_dict = dict()
        for num in file_dict.keys():
            file_queue = file_dict.get(num)
            block_dict.setdefault(num)
            block_dict[num] = read_block(file_queue.popleft())
        output_block = []
        compare_block = []
        for num in block_dict.keys():
            key_queue = block_dict.get(num)
            compare_block.append(key_queue.popleft())
        while True:
            if len(output_block) == block_size:
                write_block(output_block)
                output_block.clear()
            key_min = sorted(compare_block)[0]
            if key_min == sys.maxsize:
                write_block(output_block)
                return
            output_block.append(key_min)
            location = compare_block.index(key_min) + 1
            key_queue = block_dict.get(location)
            if key_queue is None:
                compare_block[location - 1] = sys.maxsize
            else:
                compare_block[location - 1] = key_queue.popleft()
            if not key_queue:
                file_queue = file_dict.get(location)
                if len(file_queue) != 0:
                    block_dict[location] = read_block(file_queue.popleft())
                else:
                    block_dict[location] = None


if __name__ == '__main__':
    split()
    merge()
