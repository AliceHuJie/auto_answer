# -*- coding: utf-8 -*-
# @Time    : 2018/11/2 15:14
# @Author  : hujie
# @Info  : 主要完成由问题到查询语句的转化

from kbqa.spar_query_temp import QuestionSet   # 不能删除该行，动态调用时会用到
from kbqa import word_tagging
from keras.models import load_model
from kbqa.data_helper import load_tokenizer, MAX_SEQUENCE_LENGTH
from keras.preprocessing.sequence import pad_sequences
import os

# 类别与生成该类别问题的函数对应
LABEL_TEMP_MAP = {
    0: 'movie_rating_question',   # 电影评分
    1: 'movie_showtime_question',  # 上映时间
    2: 'movie_type_question',  # 电影风格
    3: 'movie_intro_question',  # 电影剧情
    4: 'has_actor_question',  # 某电影有哪些演员
    5: 'actor_intro_question',  # 演员简介
    6: 'type_movie_by_actor_question',  # 演员演过的某类型的电影有哪些
    7: 'has_movie_question',  # 演员演过哪些电影
    8: 'movie_gt_by_actor_question',  # 演员演过的高于多少分的电影
    9: 'movie_lt_by_actor_question',  # 演员演过的低于多少分的电影
    10: 'movie_type_by_actor_question',  # 演员演过哪些电影类型
    11: 'movies_by_cooperate_question',  # A,B合作演出的电影有哪些
    12: 'how_many_movie_by_actor_question',  # 演员演过多少部电影
    13: 'actor_birthday_question',  # 演员生日
    14: 'movie_all_info_question',  # 电影的详细信息
}
cur_path = os.path.dirname(os.path.abspath(__file__))
model_name = 'word_vector_cnn_model.h5'  # 使用的分类模型的名字 cnn_model.h5 word_vector_cnn_model.h5
model_path = os.path.abspath(os.path.join(cur_path, '..\\data\\model'))
model_file = '\\'.join([model_path, model_name])

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
        问句分类，找到匹配的模板，再进行关键槽位的填充，返回对应的SPARQL查询语句
        :param question:
        :return:
        """
        word_objects = self.tw.get_word_objects(question)
        words_list = self.tw.get_cut_words(question)
        label = self.predict(words_list)
        print(label)
        func = 'QuestionSet.' + LABEL_TEMP_MAP[label]
        print(func)
        sparql = fun_call(function_name=func, word_objects=word_objects)
        return sparql

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
        return label[0]


def fun_call(function_name, word_objects):
    return eval(function_name)(word_objects)  # 根据函数名动态调用


if __name__ == '__main__':
    ques = [u'电影功夫之王有哪些演员？', u'成龙演过什么电影？', u'电影功夫之王有哪些演员？', u'电影功夫之王有哪些演员？']
    q2s = Question2Sparql()
    for q in ques:
        my_query = q2s.get_sparql(q)
        print(my_query)