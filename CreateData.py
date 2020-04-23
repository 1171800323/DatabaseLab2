import datetime
import os
import random

address = os.path.abspath(os.path.join(os.getcwd(), "./."))
data_path = address + '/data.csv'

# 生成1000000条数据，花费大约33s
startTime = datetime.datetime.now()

total = 1000000
output = ''
for index in range(0, total):
    A = random.randint(1, total)
    B = ''
    for i in range(0, 12):
        B += chr(random.randint(97, 122))
    output += str(A) + ',' + B + '\n'

endTime = datetime.datetime.now()
print(str((endTime - startTime).seconds) + 's')

with open(data_path, 'w', encoding='utf-8') as f:
    f.write(output)
