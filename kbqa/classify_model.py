# -*- coding: utf-8 -*-
# @Time    : 2018/10/31 20:35
# @Author  : hujie
# @Info  : 各种分类模型的训练

import pickle

import matplotlib.pyplot as plt
import numpy as np
from gensim.models import word2vec
from keras.layers import Conv1D, MaxPooling1D, Embedding
from keras.layers import Dense, Flatten, Dropout, LSTM
from keras.models import Sequential
from keras.utils import plot_model
from sklearn import metrics
from sklearn.externals import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC

from kbqa.data_helper import load_tokenizer, MAX_SEQUENCE_LENGTH, load_data, onehot_to_category

EMBEDDING_DIM = 100  # 每个词对应的词向量的维度
model_path = '../data/classify_model/'
tokenizer, word_index = load_tokenizer()
w2v_model_path = '../data/w2v_model/movie_field.model'
predict_output_path = '../data/classify_data/predict_output/'
compare_png_path = '../data/classify_data/compare_pngs/'
# 要比较的模型
model_name_list = ['cnn', 'cnn_w2c', 'lstm', 'lstm_w2c', 'mlp', 'lr_1', 'lr_2', 'nb_1', 'nb_2', 'svm_1', 'svm_2']


def train_cnn_classify():
    """
    没有利用word2vec的cnn
    :return: null，但是保存了模型
    """
    model_name = ''.join([model_path, 'cnn_model.h5'])
    model_pic = ''.join([model_path, 'cnn.png'])

    x_train, y_train, x_val, y_val, x_test, y_test = load_data()  # 加载训练测试数据

    model = Sequential()
    model.add(Embedding(len(word_index) + 1, EMBEDDING_DIM, input_length=MAX_SEQUENCE_LENGTH))
    model.add(Dropout(0.2))
    model.add(Conv1D(250, 3, padding='valid', activation='relu', strides=1))
    model.add(MaxPooling1D(3))
    model.add(Flatten())
    model.add(Dense(EMBEDDING_DIM, activation='relu'))
    model.add(Dense(y_train.shape[1], activation='softmax'))
    model.summary()

    plot_model(model, to_file=model_pic, show_shapes=True)
    model.compile(loss='categorical_crossentropy',
                  optimizer='rmsprop',
                  metrics=['acc'])
    model.fit(x_train, y_train, validation_data=(x_val, y_val), epochs=30, batch_size=128)
    model.save(model_name)
    # print(model.evaluate(x_test, y_test))   # 输出整体的loss 和 accuracy, 形如：[1.579357478227565, 0.5428571428571428]
    y_preds = model.predict_classes(x_test)  # 输出的具体的类别
    y_scores = model.predict(x_test)  # 输出的是概率，等价于predict_proba
    save_predict_output(y_test, y_preds, y_scores, 'cnn')


def train_cnn_w2v_classify():
    """
    将预训练的 word2vec嵌入cnn的embedding层
    :return: null，但是保存了模型
    """
    model_name = ''.join([model_path, 'word_vector_cnn_model.h5'])
    model_pic = ''.join([model_path, 'word_vector_cnn.png'])

    x_train, y_train, x_val, y_val, x_test, y_test = load_data()  # 加载训练测试数据

    w2v_model = word2vec.Word2Vec.load(w2v_model_path)
    embedding_matrix = np.zeros((len(word_index) + 1, EMBEDDING_DIM))
    for word, i in word_index.items():
        if word in w2v_model:
            embedding_matrix[i] = np.asarray(w2v_model[word], dtype='float32')
    embedding_layer = Embedding(len(word_index) + 1,
                                EMBEDDING_DIM,
                                weights=[embedding_matrix],
                                input_length=MAX_SEQUENCE_LENGTH,
                                trainable=False)
    model = Sequential()
    model.add(embedding_layer)
    model.add(Dropout(0.2))
    model.add(Conv1D(250, 3, padding='valid', activation='relu', strides=1))
    model.add(MaxPooling1D(3))
    model.add(Flatten())
    model.add(Dense(EMBEDDING_DIM, activation='relu'))
    model.add(Dense(y_train.shape[1], activation='softmax'))
    model.summary()

    plot_model(model, to_file=model_pic, show_shapes=True)
    model.compile(loss='categorical_crossentropy',
                  optimizer='rmsprop',
                  metrics=['acc'])
    model.fit(x_train, y_train, validation_data=(x_val, y_val), epochs=30, batch_size=128)
    model.save(model_name)
    # print(model.evaluate(x_test, y_test))
    y_preds = model.predict_classes(x_test)
    y_scores = model.predict(x_test)
    save_predict_output(y_test, y_preds, y_scores, 'cnn_w2c')
    # 是否保存历史
    # if save_history is True:
    #     history_path = ''.join([model_path, 'word_vector_cnn_model.history'])
    #     with open(history_path, 'wb') as handle:
    #         pickle.dump(history, handle, protocol=pickle.HIGHEST_PROTOCOL)


def train_lstm_classify():
    """
    不带w2v预训练词向量的LSTM分类模型
    :return: 
    """
    model_name = ''.join([model_path, 'lstm_model.h5'])
    model_pic = ''.join([model_path, 'lstm.png'])

    x_train, y_train, x_val, y_val, x_test, y_test = load_data()  # 加载训练测试数据

    model = Sequential()
    model.add(Embedding(len(word_index) + 1, EMBEDDING_DIM,
                        input_length=MAX_SEQUENCE_LENGTH))
    model.add(LSTM(200, dropout=0.2, recurrent_dropout=0.2))
    model.add(Dropout(0.2))
    model.add(Dense(y_train.shape[1], activation='softmax'))
    model.summary()
    plot_model(model, to_file=model_pic, show_shapes=True)
    model.compile(loss='categorical_crossentropy',
                  optimizer='rmsprop',
                  metrics=['acc'])
    model.fit(x_train, y_train, validation_data=(x_val, y_val), epochs=30, batch_size=128)
    model.save(model_name)
    # print(model.evaluate(x_test, y_test))
    y_preds = model.predict_classes(x_test)
    y_scores = model.predict(x_test)
    save_predict_output(y_test, y_preds, y_scores, 'lstm')


def train_w2v_lstm_classify():
    """
    使用预训练词向量的LSTM
    :return: 
    """
    model_name = ''.join([model_path, 'word_vector_lstm_model.h5'])
    model_pic = ''.join([model_path, 'word_vector_lstm.png'])
    x_train, y_train, x_val, y_val, x_test, y_test = load_data()  # 加载训练测试数据

    w2v_model = word2vec.Word2Vec.load(w2v_model_path)
    embedding_matrix = np.zeros((len(word_index) + 1, EMBEDDING_DIM))
    for word, i in word_index.items():
        if word in w2v_model:
            embedding_matrix[i] = np.asarray(w2v_model[word], dtype='float32')
    embedding_layer = Embedding(len(word_index) + 1,
                                EMBEDDING_DIM,
                                weights=[embedding_matrix],
                                input_length=MAX_SEQUENCE_LENGTH,
                                trainable=False)

    model = Sequential()
    model.add(embedding_layer)
    model.add(LSTM(200, dropout=0.2, recurrent_dropout=0.2))
    model.add(Dropout(0.2))
    model.add(Dense(y_train.shape[1], activation='softmax'))
    model.summary()

    plot_model(model, to_file=model_pic, show_shapes=True)
    model.compile(loss='categorical_crossentropy',
                  optimizer='rmsprop',
                  metrics=['acc'])
    model.fit(x_train, y_train, validation_data=(x_val, y_val), epochs=30, batch_size=128)
    model.save(model_name)
    # print(model.evaluate(x_test, y_test))
    y_preds = model.predict_classes(x_test)
    y_scores = model.predict(x_test)
    save_predict_output(y_test, y_preds, y_scores, 'lstm_w2c')


def train_mlp():
    """
    :return: 
    """
    x_train, y_train, x_val, y_val, x_test, y_test = load_data(1)  # 加载训练测试数据
    model_name = ''.join([model_path, 'mlp_model.h5'])
    model = Sequential()
    model.add(Dense(512, input_shape=(200,), activation='relu'))  # len(word_index) + 1,
    model.add(Dropout(0.2))
    model.add(Dense(y_train.shape[1], activation='softmax'))
    model.summary()
    model.compile(loss='categorical_crossentropy',
                  optimizer='rmsprop',
                  metrics=['acc'])
    model.fit(x_train, y_train, validation_data=(x_val, y_val), epochs=30, batch_size=128)
    model.save(model_name)
    # print(model.evaluate(x_test, y_test))
    y_preds = model.predict_classes(x_test)
    y_scores = model.predict(x_test)
    save_predict_output(y_test, y_preds, y_scores, 'mlp')


def train_nb_1():
    """
    method = 1 
    朴素贝叶斯方法进行多分类，输入的每个句子是tfidf表示的一维向量，输出是概率最大的类别数字
    :return: 
    """
    x_train, y_train, x_val, y_val, x_test, y_test = load_data(1)  # 加载训练测试数据
    model = MultinomialNB(alpha=0.01)
    y_train = onehot_to_category(y_train)
    model.fit(x_train, y_train)
    y_preds = model.predict(x_test)
    y_scores = model.predict_proba(x_test)
    print(metrics.classification_report(onehot_to_category(y_test), y_preds))
    save_predict_output(y_test, y_preds, y_scores, 'nb_1')
    '''
    9.0
    [4.32567516e-19 3.03658267e-20 1.22293838e-17 4.20375343e-20
     4.16862317e-17 2.89950369e-19 4.06820135e-16 5.28648267e-18
     1.21576708e-19 1.00000000e+00 5.07273458e-17 2.15807347e-17
     1.04050428e-15 6.07141102e-19 6.86716787e-17 4.53780780e-18
     1.91646627e-19 2.07101492e-19 7.88003566e-22 4.69237676e-22
     6.70152763e-22 2.80486008e-18]
     '''


def train_nb_2():
    """
    method = 1 
    朴素贝叶斯方法进行多分类，输入的每个句子是tfidf表示的一维向量，输出是概率最大的类别数字
    :return: 
    """
    x_train, y_train, x_val, y_val, x_test, y_test = load_data(2)  # 加载训练测试数据
    model = MultinomialNB(alpha=0.01)
    y_train = onehot_to_category(y_train)
    model.fit(x_train, y_train)
    y_preds = model.predict(x_test)
    y_scores = model.predict_proba(x_test)
    save_predict_output(y_test, y_preds, y_scores, 'nb_2')
    print(metrics.classification_report(onehot_to_category(y_test), y_preds))



def train_svm_1():
    x_train, y_train, x_val, y_val, x_test, y_test = load_data(1)  # 加载训练测试数据
    svm = SVC(kernel='linear', probability=True)
    y_train = onehot_to_category(y_train)
    svm.fit(x_train, y_train)
    y_preds = svm.predict(x_test)
    y_scores = svm.predict_proba(x_test)  # 以一个测试为例，看一下决策距离的对应结果是什么
    save_predict_output(y_test, y_preds, y_scores, 'svm_1')
    print(metrics.classification_report(onehot_to_category(y_test), y_preds))
    model_name = ''.join([model_path, 'svm.m'])
    joblib.dump(svm, model_name)


def train_svm_2():
    x_train, y_train, x_val, y_val, x_test, y_test = load_data(2)  # 加载训练测试数据
    svm = SVC(kernel='linear', probability=True)
    y_train = onehot_to_category(y_train)
    svm.fit(x_train, y_train)
    y_preds = svm.predict(x_test)
    y_scores = svm.predict_proba(x_test)  # 以一个测试为例，看一下决策距离的对应结果是什么
    save_predict_output(y_test, y_preds, y_scores, 'svm_2')
    print(metrics.classification_report(onehot_to_category(y_test), y_preds))

def train_lr_1():
    """
    method = 1， 数据是0、1组成的向量
    :return: 
    """
    x_train, y_train, x_val, y_val, x_test, y_test = load_data(1)  # 加载训练测试数据
    y_train = onehot_to_category(y_train)
    lr = LogisticRegression(multi_class='multinomial', solver='lbfgs')
    lr.fit(x_train, y_train)
    y_preds = lr.predict(x_test)
    y_scores = lr.predict_proba(x_test)
    print(metrics.classification_report(onehot_to_category(y_test), y_preds))
    save_predict_output(y_test, y_preds, y_scores, 'lr_1')


def train_lr_2():
    """
    method = 2, 输入是tf-idf向量
    :return: 
    """
    x_train, y_train, x_val, y_val, x_test, y_test = load_data(2)  # 加载训练测试数据
    y_train = onehot_to_category(y_train)
    lr = LogisticRegression(multi_class='multinomial', solver='lbfgs')
    lr.fit(x_train, y_train)
    y_preds = lr.predict(x_test)
    y_scores = lr.predict_proba(x_test)
    print(metrics.classification_report(onehot_to_category(y_test), y_preds))
    save_predict_output(y_test, y_preds, y_scores, 'lr_2')


def plot(history_name):
    """
    单独使用保存的history对象来画图而不是训练直接画图，节省后续想画图时再去训练模型的时间
    :param history_name: 
    :return: 
    """
    history_path = ''.join([model_path, history_name])
    with open(history_path, 'rb') as f:
        history = pickle.load(f)
    plt.style.use("ggplot")
    plt.figure()
    plt.plot(history.epoch, history.history["loss"], label="train_loss")
    plt.plot(history.epoch, history.history["acc"], label="train_acc")
    plt.plot(history.epoch, history.history["val_loss"], label="val_loss")
    plt.plot(history.epoch, history.history["val_acc"], label="val_acc")
    plt.show()


def plot_roc(model_list, fpr, tpr, auc):
    """
    根据各模型的相应数据指标，绘制各自的roc曲线在同一个图中便于比较
    :param model_list: 
    :param fpr: 
    :param tpr: 
    :param auc: 
    :return: 
    """
    print('Roc Curve...')
    styles = ['r', 'g', 'b', 'c', 'm', 'y', 'k', 'r--', 'g--', 'b--', 'c--', 'm--', 'y--', 'k--']
    plt.figure(1)
    models_count = len(model_list)
    for i, color in zip(range(models_count), styles[:models_count]):
        m = model_list[i].split('_model')[0]
        plt.plot(fpr[i], tpr[i], styles[i], lw=2, alpha=0.7, label=u'%s : AUC=%.3f' % (m, auc[i]))
    plt.plot((0, 1), (0, 1), c='#808080', lw=1, ls='--', alpha=0.7)
    plt.xlim((-0.01, 1.02))
    plt.ylim((-0.01, 1.02))
    plt.xticks(np.arange(0, 1.1, 0.1))
    plt.yticks(np.arange(0, 1.1, 0.1))
    plt.xlabel('False Positive Rate', fontsize=13)
    plt.ylabel('True Positive Rate', fontsize=13)
    plt.grid(b=True, ls=':')
    plt.legend(loc='lower right', fancybox=True, framealpha=0.8, fontsize=12)
    plt.title(u'ROC and AUC', fontsize=17)
    # plt.show()
    plt.savefig(compare_png_path + 'roc.png')
    print('ROC - Curve saved ... ')

def plot_pr(model_list, recall, precision, average_precision):
    """
    根据模型list以及各自的recall，precision,average_precision数据绘图
    :param model_list: 
    :param recall: 
    :param precision: 
    :param average_precision: 
    :return: 
    """
    print('P-R Curve...')
    styles = ['r', 'g', 'b', 'c', 'm', 'y', 'k', 'r--', 'g--', 'b--', 'c--', 'm--', 'y--', 'k--']
    plt.figure()
    models_count = len(model_list)
    for i, color in zip(range(models_count), styles[:models_count]):
        m = model_list[i]
        plt.plot(recall[i], precision[i], styles[i], alpha=0.7, label=u'%s : avr_precision=%.3f'
                                                                        % (m, average_precision[i]))
    plt.ylim([0.0, 1.05])
    plt.xlim([0.0, 1.0])
    plt.xticks(np.arange(0, 1.1, 0.1))
    plt.yticks(np.arange(0, 1.1, 0.1))
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.legend(loc='lower right', fancybox=True, framealpha=0.8, fontsize=12)
    plt.title('Average precision score, micro-averaged over all classes')
    # plt.show()
    plt.savefig(compare_png_path + 'pr.png')
    print('PR - Curve saved ... ')


def save_predict_output(y_test, y_preds, y_scores, filename):
    """
    保存模型的预测输出到对应文件中
    :param y_test: 测试数据的真实标签
    :param y_preds: 测试数据的预测值/one-hot向量
    :param y_scores: 测试数据类别概率输出
    :param filename: 文件名
    :return: None
    """
    file = predict_output_path + filename
    with open(file, 'wb') as handle:
        obj = (y_test, y_preds, y_scores)
        pickle.dump(obj, handle, protocol=pickle.HIGHEST_PROTOCOL)


def read_predict_output(filename):
    """
    从指定文件中读出相应模型的预测输出
    :param filename: 每个模型有其对于的输出文件
    :return: y_test, y_preds, y_scores
    """
    file = predict_output_path + filename
    with open(file, 'rb') as f:
        (y_test, y_preds, y_scores) = pickle.load(f)
    return y_test, y_preds, y_scores


def compare_model(model_list):
    """
    对比模型的分类效果，把要比较的模型的ROC, PR曲线分别画在一张图中
    各模型训练完都会预测，把各自的y_test, y_preds, y_score保存下来。pickle保存
    这里加载要比较的模型的这些数据，再进行画图比较
    :param model_list: 要比较的模型名字列表，也就对应其输出的文件名
    :return: 
    """
    fpr = dict()
    tpr = dict()
    auc = dict()
    precision = dict()
    recall = dict()
    average_precision = dict()
    models_count = len(model_list)

    for i in range(models_count):
        y_true, y_preds, y_scores = read_predict_output(model_list[i])
        # 观察每个分类模型的结果报告和混淆矩阵
        # print('Model: ' + str(model_name_list[i]).upper())
        # print('Classification Report...')
        # print(metrics.classification_report(y_true, y_preds))
        # print('Confusion Matrix...')
        # print(metrics.confusion_matrix(y_true, y_preds))
        fpr[i], tpr[i], thresholds = metrics.roc_curve(y_true.ravel(), y_scores.reshape(-1, 1).ravel())
        # y_true 是one_hot, y_scores, micro 方式计算fpr, tpr, threshold
        auc[i] = metrics.auc(fpr[i], tpr[i])   # 手动计算auc
        # auc2 = metrics.roc_auc_score(y_true, y_preds, average='micro')  # 直接由预测结果和真实结果调用函数计算auc

        precision[i], recall[i], thresholds = metrics.precision_recall_curve(y_true.ravel(), y_scores.ravel())
        average_precision[i] = metrics.average_precision_score(y_true, y_scores, average="micro")

    plot_roc(model_list, fpr, tpr, auc)
    plot_pr(model_list, recall, precision, average_precision)


def compare_report(model_list, report=True, comfusion_matrix=False):
    for model in model_list:
        print('Model: ' + model)
        if report is True:
            y_true, y_preds, y_scores = read_predict_output(model)
            if model in['cnn', 'cnn_w2v', 'lstm', 'lstm_w2v', 'mlp']:
                print(metrics.classification_report(onehot_to_category(y_true), y_preds))
            else:
                print(metrics.classification_report(onehot_to_category(y_true), y_preds))
        if comfusion_matrix is True:
            if model in['cnn', 'cnn_w2v', 'lstm', 'lstm_w2v', 'mlp']:
                print(metrics.confusion_matrix(onehot_to_category(y_true), y_preds))
            else:
                print(metrics.confusion_matrix(onehot_to_category(y_true), y_preds))


if __name__ == '__main__':
    # train_cnn_classify()
    # train_cnn_w2v_classify()
    # train_lstm_classify()
    # train_w2v_lstm_classify()
    # train_mlp()
    # train_nb_1()
    # train_nb_2()
    # train_svm_1()
    # train_svm_2()
    # train_lr_1()
    # train_lr_2()
    compare_model(model_name_list[5:])
    # print(model_name_list[5:])
    # compare_report(model_name_list[5:])
