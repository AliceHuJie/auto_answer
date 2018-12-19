# -*- coding: utf-8 -*-
# @Time    : 2018/10/19 12:19
# @Author  : hujie
# @Info  : 生成分类训练数据

import os
import re

import numpy as np
import pandas as pd

from kbqa.word_tagging import Tagger, Word

movie_name_df = pd.read_table('../data/movie.txt', header=None, sep=" ", encoding='utf-8')
actor_name_df = pd.read_table('../data/name2.txt', header=None, sep=" ", encoding='utf-8')   # name2 增加了外文名
genre_name_df = pd.read_table('../data/genres.txt', header=None, sep=" ", encoding='utf-8')
number_value_df = pd.read_table('../data/number2.txt', header=None, sep=" ", encoding='utf-8')  # number2中的分数增加了中文表达
language_value_df = pd.read_table('../data/language.txt', header=None, sep=" ", encoding='utf-8', error_bad_lines=False)
region_value_df = pd.read_table('../data/region.txt', header=None, sep=" ", encoding='utf-8', error_bad_lines=False)
year_value_df = pd.read_table('../data/year.txt', header=None, sep=" ", encoding='utf-8', error_bad_lines=False)

movie_name_array = np.array(movie_name_df[0])
actor_name_array = np.array(actor_name_df[0])
genre_name_array = np.array(genre_name_df[0])
number_value_array = np.array(number_value_df[0])
language_name_array = np.array(language_value_df[0])
region_name_array = np.array(region_value_df[0])
year_value_array = np.array(year_value_df[0])


def is_chinese_name(check_name):
    """
    判断人名是否是中文名,只包含中文，暂时不处理外文名以及  安娜.卡列罗娜的情况
    :param check_name:  
    :return: 
    """
    index = check_name.find('·')
    if index == -1:
        return True
    return False


def is_recognizable_movie_name(check_movie_name):
    """
    判断电影名是否可识别。剔除不能切词识别的电影名。把可识别的去构造问题作为训练数据
    :param check_movie_name:  
    :return: 
    """
    temp_name = re.findall(r'[\u4e00-\u9fa5a-zA-Z0-9]', check_movie_name)  # 提取去掉所有字符后的电影名称
    if len(check_movie_name) == len(temp_name):   # 两个长度相同，说明电影名不包含字符，只含字符数字中文
        return True
    return False


def get_all_chinese_name():
    """
    从人名文件中拿到所有中文名的人，保存到name文件中
    11.13日修改了，得到外文名+中文名
    :return: 
    """
    name_list = pd.read_table('./user_dicts/person_name.txt', header=None, sep=" ", encoding='utf-8')
    array = np.array(name_list[0])  # 取第一列，也就是人名
    # new_name_list = filter(is_chinese_name, array)   # 返回值是iter
    # print(list(new_name_list))   # iter变list打印
    # new_array = np.array(list(new_name_list))   # list 转为np.array
    # print(new_array)
    data = pd.DataFrame(array)  # np.array 转 df
    data.to_csv('../data/name2.txt', index=False, header=False)  # df 保存到文件中


def get_all_recognizable_movie_name():
    """
    从电影名文件中拿到所有可识别的电影名去作为构建问句后的训练数据
    :return: 
    """
    movie_list = pd.read_table('./user_dicts/movie_title.txt', header=None, sep=" ", encoding='utf-8')
    array = np.array(movie_list[0])  # 取第一列，也就是电影名
    new_movie_list = filter(is_recognizable_movie_name, array)   # 返回值是iter
    # print(list(new_movie_list))   # iter变list打印
    new_array = np.array(list(new_movie_list))   # list 转为np.array
    # print(new_array)
    data = pd.DataFrame(new_array)  # np.array 转 df
    data.to_csv('../data/movie.txt', index=False, header=False)  # df 保存到文件中


def get_random_score():
    """
    生成一个随机数，范围在0-10，精度最多一位小数。 
    【注意，项目中该文件在是生成后，还手动加了几个整数，比如 3.0 后加了一个3】
    :return: 
    """
    number_list = []
    k = 0.0
    while k <= 10:
        num = round(k, 2)
        number_list.append(str(num))
        k = k + 0.1
    k1 = 0
    while k1 <= 10:
        number_list.append(str(k1))
        k1 = k1 + 1
    number_list.sort()
    new_array = np.array(number_list)  # list 转为np.array
    # print(new_array)
    data = pd.DataFrame(new_array)  # np.array 转 df
    data.to_csv('../data/number.txt', index=False, header=False)  # df 保存到文件中


def get_tag_by_filename(filename):
    """
    获取问题模板文件名中的数字序号，也就是问题的分类
    比如【0】评分.txt  该类问题的分类号就是0
    :return: 
    """
    index = filename.index("】")
    seq_tag = filename[1:index]
    # print(seq_tag)
    return seq_tag


def generate_all_question_temp():
    """
     question/*.txt  =》 all_question_temp.txt
     汇聚所有的问题模板到一个文件中，并打上tag分类标签
    """

    path = '../data/question/'
    files = os.listdir(path)
    df = pd.DataFrame(columns=['question_temp', 'tag'])
    for file in files:
        tag = get_tag_by_filename(file)
        file = path + file
        res = open(file, 'r', encoding='UTF-8')
        a_df = pd.read_table(res, header=None, names=['question_temp'], sep=" ", encoding='utf-8')
        a_df['tag'] = tag
        df = df.append(a_df, ignore_index=True)
    df.to_csv('../data/all_question_temp.txt', header=False, sep=' ')
    print(df)


def generate_train_data():
    """
        问句构建
        all_question_temp.txt =>  tagged_data.txt
        根据各种问题模板，把模板中的nr 替换成随机的真实人名， nz 替换成真实电影名。
        并根据问题类别打上标签，再存入tagged_data.txt 中
    :return: 
    """
    ques_temp_df = pd.read_table('../data/all_question_temp.txt', header=None, sep=" ", encoding='utf-8')
    with open('../data/tagged_data.txt', 'a+', encoding='utf8') as f:
        for index in ques_temp_df.index:   # 逐行遍历数据
            temp = ques_temp_df.iloc[index, 1]
            tag = ques_temp_df.iloc[index, 2]
            line = fill_question(temp) + ' ' + str(tag) + '\n'
            f.write(line)


def fill_question(ques_temp):
    """
    传入一个模板，去生成具体的问句，被generate_train_data调用
    :param ques_temp: 一句问题模板
    :return: 填充后的实际问题
    """
    question = ques_temp
    if question.find('nr') != -1:
        question = question.replace('nr', np.random.choice(actor_name_array), 1)
    if question.find('nr') != -1:  # 替换完一个人名还有一个
        question = question.replace('nr', np.random.choice(actor_name_array), 1)
    if question.find('nz') != -1:  # 替换电影名
        question = question.replace('nz', np.random.choice(movie_name_array))
    if question.find('ng') != -1:  # 替换类型名
        question = question.replace('ng', np.random.choice(genre_name_array))
    if question.find('x') != -1:  # 替换评分值
        question = question.replace('x', str(np.random.choice(number_value_array)))
    if question.find('yy') != -1:  # 替换年份
        question = question.replace('yy', str(np.random.choice(year_value_array)))
    if question.find('ll') != -1:  # 替换语言
        question = question.replace('ll', str(np.random.choice(language_name_array)))
    if question.find('rr') != -1:  # 替换地区
        question = question.replace('rr', str(np.random.choice(region_name_array)))
    return question


def __get_questions_for_w2vtrain():
    """
    从tagged_data中取出问题那一列，保存到data/w2v/data中。就可以和其他的个人简介等内容，一起做分词和向量训练
    :return: 
    """
    # tagged_data = pd.read_table('../data/tagged_data.txt', header=None, sep=" ", encoding= 'utf-8')
    # questions = tagged_data.iloc[:, 0]
    with open('../data/w2vdata/questions.txt', 'w', encoding='utf-8') as f:
        for line in open("../data/tagged_data.txt", 'r', encoding='utf-8'):
            question = line.split(" ")[0]
            f.write(question + '\n')


def train_data_cut():
    """
    先从tagged_data中提取问题，放入question.txt 。在对问题进行切词处理
    :return: 
    """
    __get_questions_for_w2vtrain()  # 先提取出问题到
    tagger = Tagger()
    path = '../data/w2vdata/'
    output_file = open(path + 'word_cut_data.txt', 'w+', encoding='utf-8')
    # input_files = ['actor_introduction.txt', 'movie_introduction.txt', 'director_introduction.txt', 'questions.txt']
    input_files = ['questions.txt']
    line_num = 0
    for file_name in input_files:
        file = path + file_name
        with open(file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.replace('\\', '').replace(' ', '').strip()
                if line != '':
                    line_num += 1
                    print(line)
                    line_cut = tagger.get_cut_words(line)
                    text = ' '.join(line_cut)
                    output_file.write(text + '\n')
    output_file.close()
    print('total num :', line_num)


def text2number(word_objects):
    """
    把切词后的分数转换为数字 ，比如八点五，转成8.5
    :return: 
    """
    m = {u'点': '.', u'零': 0, u'一': 1, u'二': 2, u'三': 3, u'四': 4, u'五': 5, u'六': 6, u'七': 7, u'八': 8, u'九': 9, u'十': 10}
    new_word_objects = []
    for word in word_objects:
        if word.pos == 'ss':
            s = word.token.split(u'分')[0]
            number = ''
            for c in s:
                number = number + m.get(c)
            word.token = number
            new_word_objects.append(Word(word.token, word.pos))


def gen_annotation_questions():
    """
    生成槽位识别的标注好的训练数据
    从all_question_temp提取问题模板，填充问句的同时得到对应的标注,存入annotation_question_data.txt中
    
    比如： 
    nr 和 nr 合作的电影有哪些？ => 填充得到：
    芭芭拉 · 迪 里克森 和 袁丁 合演 的 电影 有 哪些?  => 对应的标识得到
    B-PER I-PER I-PER I-PER I-PER。。。
    :return: 
    """
    ques_temp_df = pd.read_table('../data/all_question_temp.txt', header=None, sep=" ", encoding='utf-8')
    with open('../data/ner_data/annotation_data.txt', 'a+', encoding='utf8') as f:
        for index in ques_temp_df.index:  # 逐行遍历模板问题
            temp = ques_temp_df.iloc[index, 1]
            letters, labels = fill_and_annotation_question(temp)
            lines = list(map(lambda x, y: x + ' ' + y + '\n', letters, labels))
            f.writelines(lines)
            f.write('\n')


def fill_and_annotation_question(ques_temp):
    """
    根据模板填充得到问题，同时得到对应的标注, 提供给gen_annotation_questions调用
    :param ques_temp: 问题模板
    :return: (letters, labels) 填充后问题的每个字及其对应label
    """
    question = ques_temp
    letters = []
    labels = ['O'] * len(question)  # 此时问句模板中只含nr, nz, x需要替换
    if question.find('ng') != -1:  # 替换类型名
        question = question.replace('ng', np.random.choice(genre_name_array))
    if question.find('x') != -1:  # 替换评分值
        index = question.find('x')
        num = str(np.random.choice(number_value_array))
        question = question.replace('x', num, 1)
        sub = ['B-NUM'] + ['I-NUM'] * (len(num) - 1)
        labels[index:index + 1] = sub  # x只占了一位，所以这里是加1

    while question.find('nr') != -1:  # 多个人名
        index = question.find('nr')
        actor = np.random.choice(actor_name_array)
        # actor = '丹尼尔·库德摩尔'
        question = question.replace('nr', actor, 1)
        sub = ['B-PER'] + ['I-PER'] * (len(actor) - 1)
        labels[index:index+2] = sub

    while question.find('nz') != -1:  # 替换电影名
        index = question.find('nz')
        movie = np.random.choice(movie_name_array)
        question = question.replace('nz', movie, 1)
        sub = ['B-MV'] + ['I-MV'] * (len(movie) - 1)
        labels[index:index+2] = sub

    if question.find('yy') != -1:  # 替换年份
        index = question.find('yy')
        year = np.random.choice(year_value_array)
        question = question.replace('yy', year, 1)
        sub = ['B-DATE'] + ['I-DATE'] * (len(year) - 1)
        labels[index:index + 2] = sub
    if question.find('ll') != -1:  # 替换语言
        question = question.replace('ll', str(np.random.choice(language_name_array)))
    if question.find('rr') != -1:  # 替换地区
        question = question.replace('rr', str(np.random.choice(region_name_array)))
    letters = list(map(str, question))  # 每个字的列表
    return letters, labels


if __name__ == '__main__':
    # generate_all_question_temp()
    # for i in range(10):
    #     generate_train_data()
    # for i in range(1, 59):
    #     generate_train_data()
    #     print('one time done')
    # get_questions_for_w2vtrain()
    # for i in range(10):
    #     gen_annotation_questions()
    train_data_cut()
    # get_random_score()
    # get_all_chinese_na me()
    # l, la = fill_and_annotation_question('ng类型，ll的电影有多少分数大于x')
    # print(l)
    # print(la)
