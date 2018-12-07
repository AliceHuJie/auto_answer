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

# df = pd.read_csv('./person_name.csv')
# title = df['person_name'].values
# with open('./person_name.txt', 'a', encoding='utf8') as f:
#     for t in title[1:]:
#         line = t + ' ' + 'nr' + '\n'
#         # exit(1)
#         f.write(line)


def number2text():
    """把number.txt 字典中的分值添加对应的中文读法写入该字典，用于切词切出问句中的分数
        如成龙演过的高于八点五分的电影有哪些？ 正常切词 八点五分会切成 八点 五分。现在要能够切成八点五 mm 分
    """
    m = [u'零', u'一', u'二', u'三', u'四', u'五', u'六',  u'七', u'八', u'九', u'十']
    lines = []
    for line in open("../../data/number.txt", 'r', encoding='utf-8'):
        ns = line.split('.')
        number = u'点'.join(map(lambda c: m[int(c)], ns))
        lines.append(line.strip('\n'))
        lines.append(line.strip('\n') + u'分')
        lines.append(number)
        lines.append(number + u'分')
    with open("number2.txt", 'w+', encoding='utf-8') as f:
        for line in lines:
            if line is not None:
                # f.write(line + ' ' + 'ss' + '\n')
                f.write(line + '\n')

number2text()