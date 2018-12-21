# -*- coding: utf-8 -*-
# @Time    : 2018/11/2 15:14
# @Author  : hujie
# @Info  : 主要完成由问题到查询语句的转化

import os

from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences
from sklearn.externals import joblib

from kbqa import word_tagging
from kbqa.bilsm_crf_model import annotation_slot
from kbqa.data_helper import load_tokenizer, MAX_SEQUENCE_LENGTH

# 类别与生成该类别问题的函数对应
LABEL_TEMP_MAP = {
    0: 'movie_rating_question',   # 电影评分
    1: 'movie_showtime_question',  # 上映时间
    2: 'movie_types_question',  # 电影风格
    3: 'movie_intro_question',  # 电影剧情
    4: 'movie_duration_question',  # 电影时长
    5: 'movie_alias_question',  # 电影别名
    6: 'movie_cover_question',  # 电影封面图

    7: 'actor_intro_question',  # 演员简介
    8: 'actor_birthday_question',  # 演员生日
    9: 'actor_birthplace_question',  # 演员出生地
    10: 'actor_biography_question',  # 演员星座
    11: 'actor_gender_question',  # 演员性别
    12: 'actor_pic_question',  # 演员的头像
    13: 'actor_englishname_question',  # 演员英文名

    14: 'movie_show_country_question',  # 电影在哪些国家上映了
    15: 'movie_has_director_question',  # 电影有哪些导演
    16: 'has_actor_question',  # 某电影有哪些演员
    17: 'types_of_movie_question',  # 演员演过的电影类型

    18: 'has_movie_question',  # 不含评分条件 指定条件下有哪些电影
    19: 'has_movie_gt_question',  # 评分高于多少分的电影 指定条件下有哪些电影
    20: 'has_movie_lt_question',  # 评分低于多少分的电影 指定条件下有哪些电影
    21: 'cooperate_actors_question',  # 某演员合作过的有哪些演员
}

cur_path = os.path.dirname(os.path.abspath(__file__))
model_name = 'word_vector_cnn_model.h5'  # 使用的分类模型的名字 cnn_model.h5 word_vector_cnn_model.h5 lstm_model.h5 word_vector_lstm_model.h5
model_path = os.path.abspath(os.path.join(cur_path, '..\\data\\classify_model'))
model_file = '\\'.join([model_path, model_name])
pro_threshold = 0.75  # soft 之后得到的属于各分类的概率。该阈值的设定使得softmax的最大值小于该值时判定为类别无关


class Question2Sparql:
    def __init__(self):
        print('initialize word_tagging...')
        self.tw = word_tagging.Tagger()
        print('load model...')
        self.model = load_model(model_file)
        print('load tokenizer...')
        self.tokenizer = load_tokenizer()[0]

    def get_sparql(self, question):
        """
        首先问句改写（别名，分数）
        再进行问句分类，找到匹配的模板，
        再进行关键槽位的填充，返回对应的SPARQL查询语句
        :param question: 用户的问题
        :return: 本来只需要返回sparlQL, 但是为了记录quesion即分类label， 实体识别效果等日志。添加了多余返回信息
        """
        # todo 问句的改写
        word_objects = self.tw.get_word_objects(question)
        words_list = self.tw.get_cut_words(question)
        label = self.predict(words_list)
        if label is not -1:
            func = 'QuestionSet.' + LABEL_TEMP_MAP[label]
            sparql = fun_call(function_name=func, word_objects=word_objects)
            return sparql, label, func  # TODO 待添加实体识别的结果
        return None, -1, None

    def predict(self, question_cut):
        """
        根据使用的模型，对自然语言的问句进行分类
        :param question_cut: list 分词后的问题，如：['成龙','演过', '哪些', '电影']
        :return: 分类的标签，如10
        """
        question = [' '.join(question_cut)]
        seq = self.tokenizer.texts_to_sequences(question)
        data = pad_sequences(seq, maxlen=MAX_SEQUENCE_LENGTH)
        label = self.model.predict_classes(data).astype('int')
        # output = self.model.predict(data)   # 预测的是属于每个类别的概率，结果与函数predict_proba相同
        # print(output)
        return label[0]
        # max_pro = max(output[0])
        # return label[0] if max_pro > pro_threshold else -1

    def sklearn_predict(self, question):
        """
        使用svm, nb这些普通机器学习模型来预测问句的分类
        :param question_cut: 
        :return: 
        """
        words_list = self.tw.get_cut_words(question)
        question = [' '.join(words_list)]
        tokenizer, word_index = load_tokenizer(1)
        data = tokenizer.texts_to_matrix(question)
        model_name = '\\'.join([model_path, 'svm.m'])
        model = joblib.load(model_name)
        label = model.predict(data)
        proba = model.predict_proba(data)
        # print(proba)
        return label[0]

    def get_slots(self, question):
        slots = dict()
        temp = annotation_slot(question)
        word_objects = self.tw.get_word_objects(question)
        for word in word_objects:
            if word.pos == 'ng':
                slots['genre'] = word.token
            if word.pos == 'rr':
                slots['region'] = word.token
            if word.pos == 'll':
                slots['language'] = word.token
        if temp['mv'] is not '':
            slots['movie'] = temp['mv']
        if temp['pers'] is not '':
            slots['pers'] = temp['pers']
        if temp['num'] is not '':
            slots['rate'] = temp['num']
        if temp['year'] is not '':
            slots['year'] = temp['year']
        return slots

    def rewrite_question(self, question):
        pass

def fun_call(function_name, word_objects):
    return eval(function_name)(word_objects)  # 根据函数名动态调用


if __name__ == '__main__':
    # ques = [u'成龙的英文名']
    q2s = Question2Sparql()
    # label1 = q2s.sklearn_predict(ques[0])
    # label2 = q2s.predict(ques[0])
    # print(label1, label2)
    question = '石岚和邝毅怡一起演过什么评分高于八点五分的喜剧类型的电影'
    slots = q2s.get_slots(question)
    print(slots)
    # for q in ques[:1]:
    #     my_query = q2s.get_sparql(q)
    #     print(my_query)
