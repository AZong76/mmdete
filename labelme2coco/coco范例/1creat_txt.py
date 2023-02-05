# !/usr/bin/python
# -*- coding: utf-8 -*-
import os
import random

trainval_percent = 1 # No test sample
train_percent = 0.9
jsonfilepath = 'labelme/total2017'
txtsavepath = './'
total_xml = os.listdir(jsonfilepath)

num = len(total_xml)
list = range(num)
tv = int(num * trainval_percent)
tr = int(tv * train_percent)
trainval = random.sample(list, tv)
train = random.sample(trainval, tr)

ftrainval = open('./trainval2017.txt', 'w')
ftrain = open('./train2017.txt', 'w')
fval = open('./val2017.txt', 'w')
ftest = open('./test2017.txt', 'w')  #Still create test2017.txt

for i in list:
    name = total_xml[i][:-5] + '\n'
    if i in trainval:
        ftrainval.write(name)
        if i in train:
            ftrain.write(name)
        else:
            fval.write(name)
    else:
        ftest.write(name)
ftrainval.close()
ftrain.close()
fval.close()
ftest.close()
print('Create_txt Done')


