# -*- coding: utf-8 -*-
# @Time    : 2018/10/31 20:35
# @Author  : hujie
# @Info  : 定义Word类的结构；定义Tagger类，实现自然语言转为Word对象的方法。结合词典进行分词

import jieba
import jieba.posseg as pseg
import os

from kbqa.spar_query_temp import QuestionSet

cur_path = os.path.dirname(os.path.abspath(__file__))
movie_dict_path = os.path.join(cur_path, 'user_dicts\\movie_title.txt')
name_dict_path = os.path.join(cur_path, 'user_dicts\\person_name.txt')
genre_dict_path = os.path.join(cur_path, 'user_dicts\\genre.txt')
number_dict_path = os.path.join(cur_path, 'user_dicts\\number.txt')


class Word(object):
    def __init__(self, token, pos):
        self.token = token
        self.pos = pos


class Tagger:
    def __init__(self, extra_dict_paths=None):
        # 加载自定义的词典
        my_dicts = [movie_dict_path, name_dict_path, genre_dict_path]
        for p in my_dicts:
            jieba.load_userdict(p)

        # TODO 加载外部词典
        if extra_dict_paths is not None:
            for p in extra_dict_paths:
                jieba.load_userdict(p)

        # TODO jieba不能正确切分的词语，我们人工调整其频率。
        jieba.suggest_freq(('喜剧', '电影'), True)
        jieba.suggest_freq(('恐怖', '电影'), True)
        jieba.suggest_freq(('科幻', '电影'), True)
        jieba.suggest_freq(('喜剧', '演员'), True)
        jieba.suggest_freq(('出生', '日期'), True)
        jieba.suggest_freq(('英文', '名字'), True)

    @staticmethod
    def get_word_objects(sentence):
        # type: (str) -> list
        """
        把自然语言转为Word对象
        :param sentence:
        :return:
        """
        words = [Word(word, tag) for word, tag in pseg.cut(sentence)]
        print('  '.join(list(map(lambda x, y: x + '/' + y, [w.token for w in words],
                                [w.pos for w in words]))))
        # words2 = Tagger.text2digit_number(words)  # TODO 这里只加了数字转换
        return words

    @staticmethod
    def get_cut_words(sentence):
        # type: (str) -> list
        """
        把自然语言转为切分后的词的list
        :param sentence:
        :return:
        """
        return [word for word, tag in pseg.cut(sentence)]

    @staticmethod
    def text2digit_number(word_objects):
        """
        分词后的句子进行数字分数替换 ，比如八点五，转成8.5
        :return: 
        """
        m = {u'点': '.', u'零': 0, u'一': 1, u'二': 2, u'三': 3, u'四': 4, u'五': 5, u'六': 6, u'七': 7, u'八': 8, u'九': 9, u'十': 10}
        new_word_objects = []
        number = ''
        for word in word_objects:
            if word.pos == 'ss':
                s = word.token.strip(u'分')
                for c in s:
                    if c.isdigit():
                        number += c
                    else:
                        number += str(m.get(c))
                word.token = number
            new_word_objects.append(Word(word.token, word.pos))
        return new_word_objects

    @staticmethod
    def alias2name(word_objects):
        """切词后替换问句中演员(包括外文名)，电影的别名为正名"""
        pass



if __name__ == '__main__':
    question = u"胡婕的导演"
    # words = jieba.cut(question)
    # for word in words:
    #
    #     print(word)
    # print('***********************')
    tagger = Tagger()
    words = tagger.get_word_objects(question)
    for word in words:
        print(word.token, word.pos)
    # sparl = QuestionSet.movie_show_country_question(words)
    # sparl = QuestionSet.has_actor_question(words)
    # print(sparl)