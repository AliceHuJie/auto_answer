# encoding=utf-8

"""

@author: SimmerChan

@contact: hsl7698590@gmail.com

@file: question2sparql_bak.py

@time: 2017/12/20 15:29

@desc: 将自然语言转为SPARQL查询语句

"""

from kbqa import word_tagging
from kbqa.others import question_temp_bak


class Question2Sparql:
    def __init__(self, dict_paths):
        self.tw = word_tagging.Tagger()
        # self.rules = question_temp_bak.rules

    def get_sparql(self, question):
        """
        进行语义解析，找到匹配的模板，返回对应的SPARQL查询语句
        :param question:
        :return:
        """
        word_objects = self.tw.get_word_objects(question)
        queries_dict = dict()
        print(question)
        # 用规则列表里的规则一条一条去匹配词性标注后的word objects
        for rule in self.rules[:1]:
            for word in word_objects:
                print(word.token, word.pos)
            query, num = rule.apply(word_objects)
            if query is not None:
                queries_dict[num] = query

        if len(queries_dict) == 0:
            return None
        elif len(queries_dict) == 1:
            return list(queries_dict.values())[0]
        else:
            # TODO 匹配多个语句，以匹配关键词最多的句子作为返回结果
            sorted_dict = sorted(iter(queries_dict.items()), key=lambda item: item[1])
            return sorted_dict[0][1]


# 单独测试
if __name__ == '__main__':
    q2s = Question2Sparql(['./user_dicts/movie_title.txt', './user_dicts/person_name.txt'])
    question = '成龙演过哪些电影'
    my_query = q2s.get_sparql(question.decode('utf-8'))
    print(my_query)