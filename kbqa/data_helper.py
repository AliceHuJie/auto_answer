# -*- coding: utf-8 -*-
# @Time    : 2018/10/31 18:37
# @Author  : hujie
# @Info  :  分类模型的问句预处理（基于词）：从原始问句，生成数据化的数据集，供后续embedding层使用


from kbqa.word_tagging import Tagger
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical
from sklearn.externals import joblib
import numpy as np
import pickle
import os


MAX_SEQUENCE_LENGTH = 20  # 句子的最大长度，句子转ids时，长度不足的补0
VALIDATION_SPLIT = 0.33  # 验证集的比例   训练集占0.8
TEST_SPLIT = 0.33  # 测试集的比例
cur_path = os.path.dirname(os.path.abspath(__file__))
TOKENIZER_SAVE_PATH = os.path.abspath(os.path.join(cur_path, '..\\data\\classify_data\\tokenizer.pickle'))    # 方式0使用
TOKENIZER_SAVE_PATH1 = os.path.abspath(os.path.join(cur_path, '..\\data\\classify_data\\tokenizer1.pickle'))    # 方式1使用
TOKENIZER_SAVE_PATH2 = os.path.abspath(os.path.join(cur_path, '..\\data\\classify_data\\tokenizer2.pickle'))    # 方式2使用
PADDED_IDX_DATA_LABELS = '../data/classify_data/padded_idx_train_data.pickle'   # 保存生成的训练数据的文件  句子表示成的idx,labels 是22维one-hot向量
TFIDF_DATA_LABELS = '../data/classify_data/tfidf_train_data.pickle'  # 每个句子表示成X(词典大小)个 tf-idf 值填充的向量
ONE_ZERO_DATA_LABELS = '../data/classify_data/one_zero_train_data.pickle'  # 每个句子表示成X(词典大小)个0,1 值填充的向量，0/1 代表第 j 个单词在第 i 个文档中是否出现
max_words = 200  # 用于提取特征的tokenizer保留的最高频词汇数 试过1000,200


def gen_data(method=0):
    """
    从tagged_data问题集中一行一行读取数据，把问题分词后空格连接成字符串加入questions中，label依次加入labels中
    该函数重点是保存序列化后的问题，及labels
    避免下次模型使用时，又来处理一遍原始问题生成训练集
    method: 0, 问句表示成包含的单词在词汇表中的序号，最大长度为20，比如【0，0，。。。15，6678, 90】
        问句预处理后对应保存文件： PADDED_IDX_DATA_LABELS
    method: 1, 问句表示为长度为词汇表大小的列向量，位置j为1表示该词有出现过
        问句预处理后对应保存文件： ONE_ZERO_DATA_LABELS
    method: 2, 问句表示为长度为词汇表大小的列向量，位置j的值为对应词在问句中的tf_idf值
        问句预处理后对应保存文件： TFIDF_DATA_LABELS  
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
    labels = to_categorical(np.asarray(all_labels))
    if method == 1:
        tokenizer = Tokenizer(num_words=max_words)
        tokenizer.fit_on_texts(questions)
        data = tokenizer.texts_to_matrix(questions)
        file = open(ONE_ZERO_DATA_LABELS, 'wb+')
        joblib.dump((data, labels), file, compress=3)

    elif method == 2:
        tokenizer = Tokenizer(num_words=max_words)
        tokenizer.fit_on_texts(questions)
        data = tokenizer.texts_to_matrix(questions, mode='tfidf')
        file = open(TFIDF_DATA_LABELS, 'wb+')
        joblib.dump((data, labels), file, compress=3)
    else:  # 其他都为0
        tokenizer = Tokenizer()
        tokenizer.fit_on_texts(questions)
        sequences = tokenizer.texts_to_sequences(questions)
        word_index = tokenizer.word_index
        print('Found %s unique tokens.' % len(word_index))
        # with open(TOKENIZER_SAVE_PATH, 'wb') as handle:
        #     pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)
        # print('Fitted tokenizer saved. ')
        data = pad_sequences(sequences, maxlen=MAX_SEQUENCE_LENGTH)
        file = open(PADDED_IDX_DATA_LABELS, 'wb+')
        pickle.dump((data, labels), file)
    print('Shape of data tensor:', data.shape)
    print('Shape of label tensor:', labels.shape)
    print('method = %s (data, labels) saved.' % method)
    with open(TOKENIZER_SAVE_PATH + str(method), 'wb') as handle:
        pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print('Fitted tokenizer saved. ')


def load_data(method=0):
    """
    根据method从不同的问句读取数值化后的数据，并进行打乱和训练集，测试集的划分
    根据问句中的每个词在词典中的序号将问句表示成一个长度为20的数字序列, label 变成一个列向量（label数+1）
    :return: 
    """
    files_list = [PADDED_IDX_DATA_LABELS, ONE_ZERO_DATA_LABELS, TFIDF_DATA_LABELS]
    file_name = files_list[method]   # 根据method得到要读取的文件
    # if not os.path.exists(file_name):  # 如果没有训练数据，先生成并保存到文件,根据method生成指定格式的训练数据
    #     gen_data(method)
    gen_data(method)
    file = open(file_name, 'rb')
    if method == 0:   # 0的时候是pickle的方式读取
        data, labels = pickle.load(file)
    else:   # 1,2都是joblib的方式读取
        data, labels = joblib.load(file)

    # *************************** 随机打乱data, labels ###########################################
    # n_samples = len(data)
    # sidx = np.random.permutation(n_samples)
    # data = np.array([data[s] for s in sidx])
    # labels = np.array([labels[s] for s in sidx])
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
    print('shape of X: ')
    print(np.array(x_train).shape)
    print('shape of Y: ')
    print(np.array(y_train).shape)
    # print('X like:')
    # print(x_train[0])
    return x_train, y_train, x_val, y_val, x_test, y_test


def load_tokenizer():
    """
    反序列文件中的tokenizer对象
    :return: tokenizer, word_index
    """
    method = 0   # 只有方式0会用到load_tokenizer目前
    with open(TOKENIZER_SAVE_PATH + str(method), 'rb') as f:
        tokenizer = pickle.load(f)
        word_index = tokenizer.word_index
    return tokenizer, word_index


def batch_iter():
    """
    成批生成训练数据
    :return: 
    """
    pass


def shuffle_question():
    """
    把tagged_data中的数据打乱，生成shuffled_tagged_data.txt
    :return: 
    """
    pass


def onehot_to_category(onehot):
    """
    把一个onehot向量或者矩阵(每一行都是一个onehot向量)转成具体的label
    通过与一个对角矩阵点积的方式
    比如：
    [0, 0 ,0 , 1]   *   [[1, 0, 0, 0],
                        [0, 2, 0, 0],
                        [0, 0, 3, 0],
                        [0, 0, 0, 4],]
    输入的是矩阵，即多个one-hot时就是两个矩阵的乘积
    :param onehot: 
    :return: 
    """
    metrix = [[i] for i in range(len(onehot[0]))]
    b = np.array(metrix)
    return np.dot(onehot, b).flatten()


if __name__ == '__main__':
    # x1, y1, x2, y2, x3, y3 = load_data(2)
    # print(len(x1))
    # print(onehot_to_category(y1[:10]))
    # print(y1[0])
    # gen_data()
    gen_data(1)
    gen_data(2)
