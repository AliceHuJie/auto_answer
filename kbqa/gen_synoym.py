# -*- coding: utf-8 -*-
# @Time    : 2018/12/20 17:28
# @Author  : hujie
# @Info  : 别名替换相关。对于电影名，人名，从数据库读取写到 主名-别名的映射文件
#          对于类型，地区等，自己写映射文件，映射文件最左侧是主名，右侧是多个同名称呼，用tab分开
import os
import re
import traceback

import pymysql
from sklearn.externals import joblib

data_path = 'data/synonym_data/'
# 同义词映射文件
MOVIE_SYNONYM_FILE = data_path + 'movie_synonym.txt'
PERSON_SYNONYM_FILE = data_path + 'person_synonym.txt'
GENRE_SYNONYM_FILE = data_path + 'genre_synonym.txt'
LANGUAGE_SYNONYM_FILE = data_path + 'language_synonym.txt'
REGION_SYNONYM_FILE = data_path + 'region_synonym.txt'
YEAR_SYNONYM_FILE = data_path + 'year_synonym.txt'
# 持久化保存同义词典的map
SYNONYM_DICT = data_path + 'synonym.pkl'
# 数据库提取的字段，用于后续训练词向量,需要绝对路径，不然文件会在mysql的目录下
movie_description_file = 'F:/bsworkspace/server/auto_answer_for_movie/data/w2vdata/movie_description.txt'
person_introduction_file = 'F:/bsworkspace/server/auto_answer_for_movie/data/w2vdata/person_introduction.txt'


class DBDataHelper:
    """
    清理数据库数据，利用数据库数据生成同义词典，生成电影名，人名等文件用于填充问句
    需要连接数据库的操作就定义为实例方法，其他的为类方法
    """

    def __init__(self):
        self.connect = pymysql.connect(
            host='localhost',
            port=3306,
            db='auto_answer_for_movie',
            user='root',
            passwd='2736',
            charset='utf8')
        self.cursor = self.connect.cursor()

    def gen_movie_name_map_file(self):
        sql = 'SELECT title, alias FROM auto_answer_for_movie.movie where length(title)!=char_length(title)'  # 只提取含中文的电影名
        rows = self.cursor.execute(sql)
        print('rows: ' + str(rows))
        with open(MOVIE_SYNONYM_FILE, 'w+', encoding='utf-8') as f:
            for i in range(rows):
                title, alias = self.cursor.fetchone()
                title = str(title)
                alias = str(alias)
                if alias is '':
                    continue
                for alia in DBDataHelper.extract_contains_zh_str(alias):
                    line = alia.strip() + '\t' + title.strip() + '\n'
                    f.write(line)

    def gen_person_name_map_file(self):
        sql = 'SELECT cn_name, more_cn_name FROM auto_answer_for_movie.person where length(cn_name)!=char_length(cn_name)'
        self.cursor.execute(sql)
        rows = self.cursor.execute(sql)
        print('rows: ' + str(rows))
        with open(PERSON_SYNONYM_FILE, 'w+', encoding='utf-8') as f:
            for i in range(rows):
                cn_name, more_cn_name = self.cursor.fetchone()
                cn_name = str(cn_name)
                more_cn_name = str(more_cn_name)
                if more_cn_name is '':
                    continue
                for alia in DBDataHelper.extract_contains_zh_str(more_cn_name):  # 为空提取出来就是空字典，不需要处理
                    line = alia.strip() + '\t' + cn_name.strip() + '\n'
                    f.write(line)

    def update_title_alias(self):
        """
        修改了爬虫，这个应该不需要单独运行了。
        :return: 
        """
        sql = 'SELECT movie_id, title, alias FROM auto_answer_for_movie.movie'
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            for item in results:
                movie_id, title, alias = item
                alias_extra = ''
                if len(title.split(' ')) > 0:
                    alias_extra = ' '.join(title.split(' ')[1:])
                    title = title.split(' ')[0]
                if alias_extra is not '':
                    alias = alias_extra + '/' + alias
                if alias is not '':
                    sql = 'update auto_answer_for_movie.movie set title = "{title}", alias="{alias}" where movie_id = {movie_id}'.format(
                        title=title, alias=alias, movie_id=movie_id)
                    self.cursor.execute(sql)
                    self.connect.commit()
        except Exception as e:
            traceback.print_exc(e)

    def get_description_for_w2v_train(self):
        """
        从movie表和person表读取含中文的人物介绍，电影介绍。写入文件中，后续用于训练词向量
        输出到 ../data/w2vdata/person_introduction.txt 和  ../data/w2vdata/person_description.txt 
        :return: 
        """
        sql = 'SELECT {field} FROM {table} where length({field})!=char_length({field}) into outfile "{file}"'
        movie_sql = sql.format(field='description', table='movie', file=movie_description_file)
        self.cursor.execute(movie_sql)
        person_sql = sql.format(field='introduction', table='person', file=person_introduction_file)
        self.cursor.execute(person_sql)

    @staticmethod
    def gen_year_map_file():
        m = [u'零', u'一', u'二', u'三', u'四', u'五', u'六', u'七', u'八', u'九', u'十']
        with open('./year_synonym.txt', 'w+', encoding='utf-8') as f:
            for year in range(1990, 2050):
                y1 = ''.join(map(lambda c: m[int(c)], str(year)))
                y2 = str(year)[2:]
                y3 = y1[2:]
                f.write(y1 + '\t' + str(year) + '\n')
                f.write(y2 + '\t' + str(year) + '\n')
                f.write(y3 + '\t' + str(year) + '\n')

    @staticmethod
    def extract_contains_zh_str(value):
        """
        提取别名中含有中文的别名
        在生成人和电影的别名词典时，只提取了含中文的名称。对英文不做替换
        :param value: 输入的字符串, 如江湖情未了 / 破军之战 / Circus Kid
        :return: list  [江湖情未了 ,破军之战]
        """
        zhPattern = re.compile(u'[\u4e00-\u9fa5]+')
        con_zh_list = []
        for s in value.split('/'):
            match = zhPattern.search(s)
            if match:
                con_zh_list.append(s)
        return con_zh_list

    def __del__(self):
        self.cursor.close()
        self.connect.close()


class SynonymUtils:
    """构造该类的对象，即从文件生成一个大的map文件，可以用于映射
       此外提供一些同义转换的接口，把中文数字转成数字，电影别名转成电影名等
    """

    def __init__(self):
        self.synonym_dict = {'movie': {}, 'person': {}, 'genre': {}, 'language': {}, 'region': {}, 'year': {}}
        if os.path.exists(SYNONYM_DICT):
            self.synonym_dict = joblib.load(SYNONYM_DICT)
        else:
            self.synonym_dict = SynonymUtils.generate_syn_dict()

    def rewrite_question(self, question, slot_value):
        """
        使用同义词典，对识别出的某些槽位值进行同义替换，修改槽位值。其实也就是把问句进行了改写
        :param question: 原始问题
        :param slot_value: 原始槽位数据
        :return: 改写后的(question_new, slots_new)
        """
        slot_value_new = slot_value
        for slot, value in slot_value.items():  # slot是movie， person等，person可能是list，其余是单独槽位
            if slot is 'pers':  # list中人名 依次修改
                slot_value_new[slot] = []
                for per in value:
                    new_per = self.synonym_dict['person'].get(per, per)
                    question = question.replace(per, new_per, 1)
                    slot_value_new[slot].append(new_per)
            elif slot in ['movie', 'region', 'language', 'year', 'genre']:
                new_value = self.synonym_dict[slot].get(value, value)  # 找不到同义词就保持原来的值
                slot_value_new[slot] = new_value
                question = question.replace(value, new_value, 1)
            elif slot is 'rate':
                rate = SynonymUtils.text2number(value)
                if rate is '':
                    del slot_value_new[slot]  # 删除该槽位
                else:  # 修改后的评分是数字，那就修改槽位值，以及重写问句
                    slot_value_new[slot] = rate
                    question = question.replace(value, str(rate))
        return question, slot_value_new

    @staticmethod
    def text2number(rate_str):
        """
        果转换完成的是一个数字，那就槽位修改为数字，否则槽位值就修改为空。也就是对错误提取的分数值做修正
        比如八点五，转成8.5
        @:param rate_str 分数槽位中的文本数字
        :return: 转换后的浮点数字或者''
        """
        m = {u'点': '.', u'零': 0, u'一': 1, u'二': 2, u'三': 3, u'四': 4, u'五': 5, u'六': 6, u'七': 7, u'八': 8, u'九': 9,
             u'十': 10}
        number = ''
        for c in rate_str:
            if c.isdigit():
                number += c
            else:
                number += str(m.get(c))
        try:
            rate = float(number)
            return rate
        except ValueError:
            return ''

    @staticmethod
    def generate_syn_dict():
        """生成并保存同义词典"""
        synonym_map = {'movie': {}, 'person': {}, 'genre': {}, 'language': {}, 'region': {}, 'year': {}}
        file_map = {'movie': MOVIE_SYNONYM_FILE, 'person': PERSON_SYNONYM_FILE, 'genre': GENRE_SYNONYM_FILE,
                    'language': LANGUAGE_SYNONYM_FILE, 'region': REGION_SYNONYM_FILE, 'year': YEAR_SYNONYM_FILE}
        for key, file in file_map.items():
            with open(file, 'r', encoding='utf-8') as f:
                for line in f:
                    fields = line.strip('\n').split('\t')
                    if len(fields) == 2:
                        alias, title = fields
                        synonym_map[key][alias] = title
        joblib.dump(synonym_map, SYNONYM_DICT)
        print('synonym map generated...')
        return synonym_map


def re_build_synonym_dict():
    # DBDataHelper().gen_movie_name_map_file()    # 数据库获取数据生成别名映射
    # DBDataHelper().gen_person_name_map_file()
    SynonymUtils.generate_syn_dict()  # 根据别名映射文件生成新的dict


# qq = '石岚和邝毅怡一起演过什么评分高于八点五分的搞笑类型的四川话的电影'
# slots = {'genre': '搞笑', 'pers': ['石岚', '邝毅怡'], 'rate': '八点五', 'language': '四川话'}
# q, s = SynonymUtils().rewrite_question(qq, slots)
# print(qq)
# print(q)
# print(s)

DBDataHelper().get_description_for_w2v_train()
# SynonymUtils.generate_syn_dict()
# print(SynonymUtils().synonym_dict['language'])