# -*- coding: utf-8 -*-
# @Time    : 2018/11/28 11:50
# @Author  : hujie
# @Info  : 文件说明
import numpy as np

onehot = [[0,0,0,0,0,1],[0,0,0,0,1,0],[1,0,0,0,0,0]]


def onehot_to_category(onehot):

    b = np.array([[0], [1], [2], [3], [4], [5]])
    return np.dot(onehot, b).flatten()

# r = onehot_to_category(onehot)
# print(r)

list = [[i] for i in range(22)]
print(list)