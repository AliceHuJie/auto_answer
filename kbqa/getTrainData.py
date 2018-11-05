# -*- coding: utf-8 -*-
# @Time    : 2018/10/19 12:19
# @Author  : hujie
# @Info  : 生成分类训练数据

import pandas as pd
import numpy as np
import re
import os
from kbqa.word_tagging import Tagger


movie_name_df = pd.read_table('../data/movie.txt', header=None, sep=" ")
actor_name_df = pd.read_table('../data/name.txt', header=None, sep=" ")
genre_name_df = pd.read_table('../data/genres.txt', header=None, sep=" ")
number_value_df = pd.read_table('../data/number.txt', header=None, sep=" ")
movie_name_array = np.array(movie_name_df[0])
actor_name_array = np.array(actor_name_df[0])
genre_name_array = np.array(genre_name_df[0])
number_value_array = np.array(number_value_df[0])


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
    :return: 
    """
    name_list = pd.read_table('./user_dicts/person_name.txt', header=None, sep=" ")
    array = np.array(name_list[0])  # 取第一列，也就是人名
    new_name_list = filter(is_chinese_name, array)   # 返回值是iter
    # print(list(new_name_list))   # iter变list打印
    new_array = np.array(list(new_name_list))   # list 转为np.array
    # print(new_array)
    data = pd.DataFrame(new_array)  # np.array 转 df
    data.to_csv('../data/name.txt', index=False, header=False)  # df 保存到文件中


def get_all_recognizable_movie_name():
    """
    从电影名文件中拿到所有可识别的电影名去作为构建问句后的训练数据
    :return: 
    """
    movie_list = pd.read_table('./user_dicts/movie_title.txt', header=None, sep=" ")
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
    k = 0
    while k <= 10:
        number_list.append(round(k, 2))
        k = k + 0.1
    new_array = np.array(list(number_list))  # list 转为np.array
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
        a_df = pd.read_table(res, header=None, names=['question_temp'], sep=" ")
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
    ques_temp_df = pd.read_table('../data/all_question_temp.txt', header=None, sep=" ")
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
    return question


def get_questions_from_w2vtrain():
    """
    从tagged_data中取出问题那一列，保存到data/w2v/data中。就可以和其他的个人简介等内容，一起做分词和向量训练
    :return: 
    """
    tagged_data = pd.read_table('../data/tagged_data.txt', header=None, sep=" ")
    questions = tagged_data.iloc[:, 0]
    with open('../data/w2vdata/questions.txt', 'w', encoding='utf-8') as f:
        for question in questions:
            f.write(question + '\n')


def train_data_cut():
    tagger = Tagger()
    path = '../data/w2vdata/'
    output_file = open(path + 'word_cut_data.txt', 'w+', encoding='utf-8')
    input_files = ['actor_introduction.txt', 'movie_introduction.txt', 'director_introduction.txt', 'questions.txt']
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


if __name__ == '__main__':
    for i in range(1, 50):
        generate_train_data()
        print('one time done')
