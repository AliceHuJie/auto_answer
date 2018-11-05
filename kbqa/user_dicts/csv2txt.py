# encoding=utf-8
"""
@desc:
把从mysql导出的csv文件按照jieba外部词典的格式转为txt文件。
得到电影名外部词典和人名外部词典
nz代表电影专名
nr代表人名。
"""
import pandas as pd
# df = pd.read_csv('./movie_title.csv')
# title = df['movie_title'].values

# with open('./movie_title.txt', 'a', encoding='utf8') as f:
#     for t in title[1:]:
#         line = t + ' ' + 'nz' + '\n'
#         # exit(1)
#         f.write(line)
#
# df = pd.read_csv('./movie_title.csv')
# title = df['movie_title'].values

df = pd.read_csv('./person_name.csv')
title = df['person_name'].values
with open('./person_name.txt', 'a', encoding='utf8') as f:
    for t in title[1:]:
        line = t + ' ' + 'nr' + '\n'
        # exit(1)
        f.write(line)