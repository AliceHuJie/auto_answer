# -*- coding: utf-8 -*-
# @Time    : 2018/10/31 18:37
# @Author  : hujie
# @Info  :  从原始问句，生成idx类型的数据集，供后续embedding层使用

from kbqa.word_tagging import Tagger
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical
import numpy as np
import pickle
import os


MAX_SEQUENCE_LENGTH = 20  # 句子的最大长度，句子转ids时，长度不足的补0
VALIDATION_SPLIT = 0.1  # 验证集的比例   训练集占0.8
TEST_SPLIT = 0.1  # 测试集的比例
cur_path = os.path.dirname(os.path.abspath(__file__))
TOKENIZER_SAVE_PATH = os.path.abspath(os.path.join(cur_path, '..\\data\\model\\tokenizer.pickle'))
# TOKENIZER_SAVE_PATH = '../data/model/tokenizer.pickle'  # 保存tokenizer的文件
PADDED_DATA_LABELS = '../data/model/train_data.pickle'  # 保存生成的训练数据的文件


def gen_data():
    """
    从tagged_data问题集中一行一行读取数据，把问题分词后空格连接成字符串加入questions中，label依次加入labels中
    该函数重点是保存序列化后的问题，及labels
    避免下次模型使用时，又来处理一遍原始问题生成训练集
    method: 0, 问句表示成包含的单词在词汇表中的序号，最大长度为20，比如【0，0，。。。15，6678, 90】
        问句预处理后对应保存文件： train_data.pickle
    method: 1, 问句表示为长度为词汇表大小的列向量，位置j为1表示该词有出现过
        问句预处理后对应保存文件： train_data1.pickle
    method: 2, 问句表示为长度为词汇表大小的列向量，位置j的值为对应词在问句中的tf_idf值
        问句预处理后对应保存文件： train_data2.pickle
    :return: null, 但是保存data, labels
    """
    questions = []
    all_labels = []
    tagger = Tagger()
    with open('../data/tagged_data.txt', 'r', encoding='utf8') as f:
        for line in f:  # 逐行遍历数据
            question, label = line.strip('\n').strip(' ').split(' ')
            question = ' '.join(tagger.get_cut_words(question))    # 问题的处理， TODO 如果要去除停用词，这里搞
            questions.append(question)
            all_labels.append(label)
    # return questions, labels  # 这里是全部的问题，label 集
    # ************************  问句，label 向量化得到(data, labels) *************************
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(questions)
    sequences = tokenizer.texts_to_sequences(questions)
    word_index = tokenizer.word_index
    print('Found %s unique tokens.' % len(word_index))
    with open(TOKENIZER_SAVE_PATH, 'wb') as handle:
        pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print('Fitted tokenizer saved. ')

    data = pad_sequences(sequences, maxlen=MAX_SEQUENCE_LENGTH)
    file = open(PADDED_DATA_LABELS, 'wb+')

    labels = to_categorical(np.asarray(all_labels))
    print('Shape of data tensor:', data.shape)
    print('Shape of label tensor:', labels.shape)
    pickle.dump((data, labels), file)
    print('(Padded_data, labels) saved.')


def load_data():
    """
    根据问句中的每个词在词典中的序号将问句表示成一个长度为20的数字序列, label 变成一个列向量（label数+1）
    :return: 
    """
    if not os.path.exists(PADDED_DATA_LABELS):  # 如果没有训练数据，先生成并保存到文件
        gen_data()
    file = open(PADDED_DATA_LABELS, 'rb')
    data, labels = pickle.load(file)
    # *************************** 随机打乱data, labels ###########################################
    n_samples = len(data)
    sidx = np.random.permutation(n_samples)
    data = np.array([data[s] for s in sidx])
    labels = np.array([labels[s] for s in sidx])
    # **************************** 训练集，验证集，测试集按指定比例划分 **************************
    p1 = int(len(data) * (1 - VALIDATION_SPLIT - TEST_SPLIT))
    p2 = int(len(data) * (1 - TEST_SPLIT))
    x_train = data[:p1]
    y_train = labels[:p1]
    x_val = data[p1:p2]
    y_val = labels[p1:p2]
    x_test = data[p2:]
    y_test = labels[p2:]
    print('train sentences: ' + str(len(x_train)))
    print('val sentences: ' + str(len(x_val)))
    print('test sentences: ' + str(len(x_test)))
    return x_train, y_train, x_val, y_val, x_test, y_test


def load_tokenizer():
    """
    反序列文件中的tokenizer对象
    :return: tokenizer, word_index
    """
    with open(TOKENIZER_SAVE_PATH, 'rb') as f:
        tokenizer = pickle.load(f)
        word_index = tokenizer.word_index
    return tokenizer, word_index


def batch_iter():
    """
    成批生成训练数据
    :return: 
    """
    pass


if __name__ == '__main__':
    x1, y1, x2, y2, x3, y3 = load_data()
    print(x1[0])
    print(y1[0])

