# -*- coding: utf-8 -*-
# @Time    : 2018/10/31 20:35
# @Author  : hujie
# @Info  : 定义Word类的结构；定义Tagger类，实现自然语言转为Word对象的方法。结合词典进行分词

import jieba
import jieba.posseg as pseg
import os

cur_path = os.path.dirname(os.path.abspath(__file__))
movie_dict_path = os.path.join(cur_path, 'user_dicts\\movie_title.txt')
name_dict_path = os.path.join(cur_path, 'user_dicts\\person_name.txt')


class Word(object):
    def __init__(self, token, pos):
        self.token = token
        self.pos = pos


class Tagger:
    def __init__(self, extra_dict_paths=None):
        # 加载自定义的词典
        my_dicts = [movie_dict_path, name_dict_path]
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
        return [Word(word, tag) for word, tag in pseg.cut(sentence)]

    @staticmethod
    def get_cut_words(sentence):
        # type: (str) -> list
        """
        把自然语言转为切分后的词的list
        :param sentence:
        :return:
        """
        return [word for word, tag in pseg.cut(sentence)]


if __name__ == '__main__':
    question = u"成龙演过哪些电影？"
    # tagger = Tagger()
    # words = tagger.get_word_objects(question)
    print(movie_dict_path)
    print(name_dict_path)