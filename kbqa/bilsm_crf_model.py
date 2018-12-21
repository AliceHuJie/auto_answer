import pickle

import matplotlib.pyplot as plt
import numpy as np
from keras.layers import Embedding, Bidirectional, LSTM
from keras.models import Sequential
from keras_contrib.layers import CRF

from kbqa import ner_process_data

EMBED_DIM = 100
BiRNN_UNITS = 200
EPOCHS = 3  # 训练的轮数
config_path = '../data/ner_model/config.pkl'
ner_model_path = '../data/ner_model/crf.h5'
acc_pic_path = '../data/ner_model/loss_acc.png'


def create_model(train=True):
    """
    搭建命名实体识别的模型，以及构建训练或测试的数据集
    :param train: 
    :return: 
    """
    if train:
        (train_x, train_y), (test_x, test_y), (vocab, chunk_tags) = ner_process_data.load_data()
    else:
        with open(config_path, 'rb') as inp:
            (vocab, chunk_tags) = pickle.load(inp)
    model = Sequential()
    model.add(Embedding(len(vocab), EMBED_DIM, mask_zero=True))  # Random embedding
    model.add(Bidirectional(LSTM(BiRNN_UNITS // 2, return_sequences=True)))
    crf = CRF(len(chunk_tags), sparse_target=True)
    model.add(crf)
    model.summary()
    model.compile('adam', loss=crf.loss_function, metrics=[crf.accuracy])
    if train:
        return model, (train_x, train_y), (test_x, test_y)
    else:
        return model, (vocab, chunk_tags)


def train():
    """
    利用create_model搭建好的模型及相应数据训练命名实体的识别模型，并保存训练完成的模型
    :return: 
    """
    model, (train_x, train_y), (test_x, test_y) = create_model()
    history = model.fit(train_x, train_y, batch_size=16, epochs=EPOCHS,
                        validation_data=[test_x, test_y])
    model.save(ner_model_path)

    plt.figure()
    ax_loss = plt.subplot(121)
    ax_acc = plt.subplot(122)
    plt.sca(ax_loss)
    plt.ylim(0, 10)
    plt.xlabel('epochs')
    plt.ylabel('loss')
    plt.plot(history.epoch, history.history["loss"], label="train_loss", color='red')
    plt.plot(history.epoch, history.history["val_loss"], label="val_loss", color='green')
    plt.legend(loc='lower right')
    plt.tight_layout()

    plt.sca(ax_acc)
    plt.ylim(0, 1.2)
    plt.xlabel('epochs')
    plt.ylabel('acc')
    plt.plot(history.epoch, history.history["acc"], label="train_acc", color='red')
    plt.plot(history.epoch, history.history["val_acc"], label="val_acc", color='green')

    plt.legend(loc='lower right')
    plt.tight_layout()
    plt.savefig(acc_pic_path)
    plt.show()


def annotation_slot(predict_text):
    """
    输入具体的问题，利用实体识别的模型标注出其中的人名，电影名
    :param predict_text: 要标注槽位的原始问题文本
    :return: 
    """
    model, (vocab, chunk_tags) = create_model(train=False)
    idx, length = ner_process_data.process_data(predict_text, vocab)  # 问句依靠词汇表转成idx
    model.load_weights(ner_model_path)
    raw = model.predict(idx)[0][-length:]
    result = [np.argmax(row) for row in raw]
    result_tags = [chunk_tags[i] for i in result]
    print(result_tags)

    per, mv, num, year = '', '', '', ''
    for s, t in zip(predict_text, result_tags):
        if t in ('B-PER', 'I-PER'):
            per += ' ' + s if (t == 'B-PER') else s
        if t in ('B-MV', 'I-MV'):
            mv += ' ' + s if (t == 'B-MV') else s
        if t in ('B-NUM', 'I-NUM'):
            num += ' ' + s if (t == 'B-NUM') else s
        if t in ('B-DATE', 'I-DATE'):
            year += ' ' + s if (t == 'B-DATE') else s

    if per is not '':
        per = per.strip().split(' ')

    return {
        'pers': per,
        'mv': mv.strip().split(' ')[0],
        'num': num.strip().split(' ')[0],
        'year': year.strip().split(' ')[0]
    }


if __name__ == '__main__':
    # train()
    r = annotation_slot('成龙演过的评分大于九十分的电影有什么')
    print(r)
