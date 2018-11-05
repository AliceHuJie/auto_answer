# -*- coding: utf-8 -*-
# @Time    : 2018/10/31 20:35
# @Author  : hujie
# @Info  : 各种分类模型的训练

from keras.layers import Dense, Flatten, Dropout, LSTM
from keras.layers import Conv1D, MaxPooling1D, Embedding
from keras.models import Sequential
from keras.utils import plot_model
from gensim.models import word2vec
from kbqa.data_helper import load_tokenizer, MAX_SEQUENCE_LENGTH, load_data
import numpy as np
import matplotlib.pyplot as plt
import pickle

EMBEDDING_DIM = 100  # 每个词对应的词向量的维度
model_path = '../data/model/'
tokenizer, word_index = load_tokenizer()
w2v_model_path = '../data/w2v_model/movie_field.model'
x_train, y_train, x_val, y_val, x_test, y_test = load_data()  # 加载训练测试数据


def train_cnn_classify():
    """
    没有利用word2vec的cnn
    :return: null，但是保存了模型
    """
    model_name = ''.join([model_path, 'cnn_model.h5'])
    model_pic = ''.join([model_path, 'cnn.png'])

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
    model.fit(x_train, y_train, validation_data=(x_val, y_val), epochs=2, batch_size=128)
    model.save(model_name)
    print(model.evaluate(x_test, y_test))


def train_cnn_w2v_classify():
    """
    将预训练的 word2vec嵌入cnn的embedding层
    :return: null，但是保存了模型
    """
    model_name = ''.join([model_path, 'word_vector_cnn_model.h5'])
    model_pic = ''.join([model_path, 'word_vector_cnn.png'])

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
    model.fit(x_train, y_train, validation_data=(x_val, y_val), epochs=2, batch_size=128)
    model.save(model_name)
    print(model.evaluate(x_test, y_test))

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
    model.fit(x_train, y_train, validation_data=(x_val, y_val), epochs=2, batch_size=128)
    model.save(model_name)
    print(model.evaluate(x_test, y_test))


def train_w2v_lstm_classify():
    """
    使用预训练词向量的LSTM
    :return: 
    """
    model_name = ''.join([model_path, 'word_vector_lstm_model.h5'])
    model_pic = ''.join([model_path, 'word_vector_lstm.png'])

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
    model.fit(x_train, y_train, validation_data=(x_val, y_val), epochs=2, batch_size=128)
    model.save(model_name)
    print(model.evaluate(x_test, y_test))


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

if __name__ == '__main__':
    train_cnn_classify()
    # train_cnn_w2v_classify()
    # train_lstm_classify()
    # train_w2v_lstm_classify()
    # plot('word_vector_cnn_model.history')
