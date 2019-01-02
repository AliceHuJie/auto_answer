# -*- coding: utf-8 -*-
# @Time    : 2018/12/20 12:59
# @Author  : hujie
# @Info  : 一些已有方法的组合，写到方法中，一键运行。完成所有的工作
from kbqa.data_helper import gen_data
from kbqa.get_train_data import generate_all_question_temp, generate_train_data, gen_annotation_questions


def rebuild_classify_data():
    """
    在训练测试的过程中，可能在模板问题集中增加数据。也就需要重新训练分类模型
    模板问题增加后，重新生成新的问题集，重新得到新的模型的输入数据，包括padded_data, one_zero, tfidf.
    该函数运行后，就可以去重新训练分类模型了
    :return: 
    """
    generate_all_question_temp()
    print('new all_question_temp.txt generated.\n')
    times = 30
    generate_train_data(times)
    print('new tagged_data.txt generated..\n')
    for i in range(3):
        gen_data(i)
        print('\n')


def rebuild_ner_data():
    """
    在训练测试的过程中，可能在模板问题集中增加数据。也就需要重新训练实体识别模型
    模板问题增加后，重新生成新的问题集，重新得到新的模型的标注输入数据
    该函数运行后，就可以去重新训练命名实体识别模型了
    :return: 
    """
    generate_all_question_temp()
    print('new all_question_temp.txt generated.\n')
    times = 30  # 4:1生成训练和测试数据, 训练数据8， 测试就是2份
    gen_annotation_questions(times)
    print('new annotation_data.txt generated..\n')
    print('you can rebuild ner model now...')


# rebuild_classify_data()
rebuild_ner_data()
