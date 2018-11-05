# -*- coding: utf-8 -*-
# @Time    : 2018/6/11 17:36
# @Author  : hujie
# @Info  : 文件说明将同义词字典转成属性词典
properties = set()
with open('./property.txt', 'r') as f:
    for line in f:
        for word in line.strip('\n').split(' '):
            properties.add(word)

with open('./properties.txt', 'w') as f:
    for word in properties:
        f.write(word+" pro\n")
