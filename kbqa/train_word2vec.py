# -*- coding: utf-8 -*-
# @Time    : 2018/10/22 15:23
# @Author  : hujie
# @Info  : 利用切完词的数据训练word2vec向量模型，以及如何load模型并使用
from gensim.models import word2vec


def generate_model():
    # 加载分此后的文本，使用的是Ttext2Corpus类
    sentences = word2vec.Text8Corpus('../data/w2vdata/word_cut_data.txt')
    # 训练模型，部分参数如下
    model = word2vec.Word2Vec(sentences, size=100, hs=1, min_count=5, window=5)
    model.save('../data/w2v_model/movie_field.model')


def test_model():
    model = word2vec.Word2Vec.load('../data/w2v_model/movie_field.model')
    s = model.most_similar('同性')
    # print(model.wv.vocab)
    print(s)
    # vec = model['生日']
    # print(vec)
    # print(model.wv['生日'])
    # vec = model['日期']
    # print(vec)
    # print(model.similarity('成龙', '李连杰'))

if __name__ == '__main__':
    # generate_model()
    test_model()
