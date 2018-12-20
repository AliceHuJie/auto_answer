# -*- coding: utf-8 -*-
# @Time    : 2018/12/20 17:28
# @Author  : hujie
# @Info  : 别名替换相关。对于电影名，人名，从数据库读取写到 主名-别名的映射文件
#          对于类型，地区等，自己写映射文件，映射文件最左侧是主名，右侧是多个同名称呼，用tab分开
import re
import traceback

import pymysql


class SynonymUtils:
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
        sql = 'SELECT title, alias FROM auto_answer_for_movie.movie'
        rows = self.cursor.execute(sql)
        with open('./movie_synonym.txt', 'w+', encoding='utf-8') as f:
            for i in range(30):
                title, alias = self.cursor.fetchone()
                title = title.strip()
                alias = alias.strip()
                for alia in extractContainsZhStr(alias):
                    line = alia + '\t' + title + '\n'
                    f.write(line)

    def gen_person_name_map_file(self):
        sql = 'SELECT cn_name, more_cn_name FROM auto_answer_for_movie.person'
        self.cursor.execute(sql)

    def update_title_alias(self):
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

    @classmethod
    def gen_map_file(cls):
        """
        根据类型，地区，语言，分数值，年份值，演员名，电影名几个的同名映射字典，得到一个用于句子替换的槽位表。
        并用joblib将其保存，形如：
        map = {
            per:{
            '陈港生' ： 成龙，
            ...
            },
            genre:{
            '搞笑' ： '喜剧'，
            }，
            year:{
            '08' : '2008'
            }
        }
        
        在提取了句子的槽位之后，就可以把对应槽位的值进行相应的替换。
        :return: null 
        """
        pass

    def __del__(self):
        self.cursor.close()
        self.connect.close()


def extractContainsZhStr(str):
    """
    提取别名中含有中文的别名
    在生成人和电影的别名词典时，只提取了含中文的名称。对英文不做替换
    :param str: 输入的字符串, 如江湖情未了 / 破军之战 / Circus Kid
    :return: list  [江湖情未了 ,破军之战]
    """
    zhPattern = re.compile(u'[\u4e00-\u9fa5]+')
    con_zh_list = []
    for s in str.split('/'):
        match = zhPattern.search(s)
        if match:
            con_zh_list.append(s)
    return con_zh_list


SynonymUtils().gen_movie_name_map_file()
