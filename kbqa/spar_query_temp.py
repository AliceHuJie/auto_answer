# -*- coding: utf-8 -*-
# @Time    : 2018/11/2 15:15
# @Author  : hujie
# @Info  : 各分类问题的查询语句模板

SPARQL_PREXIX = u"""
PREFIX : <http://www.auto_answer_for_movie.com#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
"""

SPARQL_SELECT_TEM = u"{prefix}\n" + \
             u"SELECT DISTINCT {select} WHERE {{\n" + \
             u"{expression}\n" + \
             u"}}\n"

SPARQL_COUNT_TEM = u"{prefix}\n" + \
             u"SELECT COUNT({select}) WHERE {{\n" + \
             u"{expression}\n" + \
             u"}}\n"

SPARQL_ASK_TEM = u"{prefix}\n" + \
             u"ASK {{\n" + \
             u"{expression}\n" + \
             u"}}\n"


def generic_movie_property(slots, movie_property):
    """
    通用的查电影属性的模板
    :param slots: 
    :param movie_property: 
    :return: 
    """
    select = u"?o"
    sparql = None
    if slots.get('movie') is not None:  # 查电影的属性，要求电影名条件不能为空
        e = u"?m :{pro} ?o. ".format(pro=movie_property)  # 查电影的属性
        e = e + generic_movie_query(slots)  # 电影的限定条件
        sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX,
                                          select=select,
                                          expression=e)
    return sparql


def generic_person_property(slots, person_property):
    """
    某演员的基本属性查询模板
    :param slots: 经识别后的槽位
    :return: 查询语句
    """
    select = u"?x"
    sparql = None
    if slots.get('pers') is not None:
        e = u"?s :personName '{person}'. " \
            u"?s :{pro} ?x".format(person=slots.get('pers')[0], pro=person_property)

        sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX,
                                          select=select,
                                          expression=e)
    return sparql


def generic_movie_query(slots):
    """
    根据槽位的限定条件，拼接查询条件
    :param slots: 
    :return: 
    """
    item = u"?m :{pro} '{pro_value}'. "
    item2 = u"?m :{pro} {pro_value}. "
    e = ''
    if slots.get('movie') is not None:
        e = e + item.format(pro='movieTitle', pro_value=slots.get('movie'))
    if slots.get('year') is not None:
        e = e + item.format(pro='movieYear', pro_value=slots.get('year'))
    if slots.get('genre') is not None:
        e = e + item2.format(pro='hasGenre', pro_value='?g')
        e = e + u" ?g :genreName '{pro_value}'. ".format(pro_value=slots.get('genre'))
    if slots.get('language') is not None:
        e = e + item2.format(pro='hasLanguage', pro_value='?l')
        e = e + u" ?l :languageName '{pro_value}'. ".format(pro_value=slots.get('language'))
    if slots.get('region') is not None:
        e = e + item2.format(pro='showInRegion', pro_value='?r')
        e = e + u" ?l :regionName '{pro_value}'. ".format(pro_value=slots.get('region'))
    if slots.get('pers') is not None:
        i = 1
        for per in slots.get('pers'):
            e = e + u"?s{i} :personName '{person}'. ?m :hasActor ?s{i} .".format(person=per, i=i)
            i = i + 1
    return e


class QuestionSet:
    def __init__(self):
        pass
        # ******************************     电影基本属性查询      ********************************
    @staticmethod
    def movie_rating_question(slots):
        """
        某电影评分是多少
        :param slots: 经识别后的槽位
        :return: 查询语句
        """
        return generic_movie_property(slots, 'movieRate')

    @staticmethod
    def movie_showtime_question(slots):
        """
        某电影上映时间是多少
        :param slots: 经识别后的槽位
        :return: 查询语句
        """
        return generic_movie_property(slots, 'movieReleaseDate')

    @staticmethod
    def movie_intro_question(slots):
        """
        某电影的剧情
        :param slots: 经识别后的槽位
        :return: 查询语句
        """
        return generic_movie_property(slots, 'movieDescription')

    @staticmethod
    def movie_duration_question(slots):
        """
        某电影时长是多少
        :param slots: 经识别后的槽位
        :return: 查询语句
        """
        return generic_movie_property(slots, 'movieRuntime')

    @staticmethod
    def movie_alias_question(slots):
        """
        某电影别名是什么
        :param slots: 经识别后的槽位
        :return: 查询语句
        """
        return generic_movie_property(slots, 'movieAlias')


    # ***********************************  非基本属性查询  **************************************

    @staticmethod
    def has_actor_question(slots):
        """
        某电影有哪些演员
        :param slots:
        :return:
        """
        select = u"?o"
        sparql = None
        if slots.get('movie') is not None:
            e = u"?m :hasActor ?a. ?a :personName ?o. "
            e = e + generic_movie_query(slots)
            sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX, select=select, expression=e)
        return sparql

    @staticmethod
    def movie_show_country_question(slots):
        """
        电影在哪些国家上映了
        :param slots: 经识别后的槽位
        :return: 查询语句
        """
        select = u"?o"
        sparql = None
        if slots.get('movie') is not None:
            e = u"?m :showInRegion ?r. ?r :regionName ?o. "
            e = e + generic_movie_query(slots)
            sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX, select=select, expression=e)
        return sparql

    @staticmethod
    def movie_has_language_question(slots):
        """
        电影有哪些语言版本
        :param slots: 经识别后的槽位
        :return: 查询语句
        """
        select = u"?o"
        sparql = None
        if slots.get('movie') is not None:
            e = u"?m :hasLanguage ?l. ?l :languageName ?o. "
            e = e + generic_movie_query(slots)
            sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX, select=select, expression=e)
        return sparql

    @staticmethod
    def movie_types_question(slots):
        """
        电影是什么风格
        :param slots: 经识别后的槽位
        :return: 查询语句
        """
        select = u"?o"
        sparql = None
        if slots.get('movie') is not None:
            e = u"?m :hasGenre ?a. ?a :genreName ?o. "
            e = e + generic_movie_query(slots)
            sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX, select=select, expression=e)
        return sparql

    @staticmethod
    def movie_has_director_question(slots):
        """
        电影有哪些导演
        :param slots: 经识别后的槽位
        :return: 查询语句
        """
        select = u"?o"
        sparql = None
        if slots.get('movie') is not None:
            e = u"?m :hasDirector ?a. ?a :personName ?o. "
            e = e + generic_movie_query(slots)
            sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX, select=select, expression=e)
        return sparql

    @staticmethod
    def movie_has_scenarists_question(slots):
        """
        电影有哪些导演
        :param slots: 经识别后的槽位
        :return: 查询语句
        """
        select = u"?o"
        sparql = None
        if slots.get('movie') is not None:
            e = u"?m :hasWriter ?a. ?a :personName ?o. "
            e = e + generic_movie_query(slots)
            sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX, select=select, expression=e)
        return sparql

    @staticmethod
    def has_movie_question(slots):
        """
        查询电影，不包含评分条件。 可选槽位：演员可以是多个，类型
        :param slots: 经识别后的槽位
        :return: 查询语句
        """
        select = u"?o"
        sparql = None
        if slots.get('pers') is not None:
            e = u"?m :movieTitle ?o. "
            e = e + generic_movie_query(slots)
            sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX, select=select, expression=e)
        return sparql

    @staticmethod
    def has_movie_gt_question(slots):
        """
        查询电影， 含大于评分条件。 可选槽位：演员可以是多个，类型
        :param slots: 经识别后的槽位
        :return: 查询语句
        """
        select = u"?o"
        sparql = None
        if slots.get('rate') is not None:
            e = u"?m :movieTitle ?o ."
            e = e + generic_movie_query(slots)
            e = e + u" ?m :movieRate ?a. Filter(?a >= {score}).".format(score=slots.get('rate'))
            sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX, select=select, expression=e)
        return sparql

    @staticmethod
    def has_movie_lt_question(slots):
        """
        查询电影， 含小于于评分条件。 可选槽位：演员可以是多个，类型
        :param slots: 经识别后的槽位
        :return: 查询语句
        """
        select = u"?o"
        sparql = None
        if slots.get('rate') is not None:
            e = u"?m :movieTitle ?o ."
            e = e + generic_movie_query(slots)
            e = e + u" ?m :movieRate ?a. Filter(?a < {score}).".format(score=slots.get('rate'))
            sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX, select=select, expression=e)
        return sparql

    @staticmethod
    def movie_count_question(slots):
        """
        查询电影的数目，不包含评分条件。 可选槽位：演员可以是多个，类型
        :param slots: 经识别后的槽位
        :return: 查询语句
        """
        select = u"?o"
        sparql = None
        if slots.get('pers') is not None:
            e = u"?m :movieTitle ?o. "
            e = e + generic_movie_query(slots)
            sparql = SPARQL_COUNT_TEM.format(prefix=SPARQL_PREXIX, select=select, expression=e)
        return sparql

    @staticmethod
    def movie_count_gt_question(slots):
        """
        查询电影的数目， 含大于评分条件。 可选槽位：演员可以是多个，类型
        :param slots: 经识别后的槽位
        :return: 查询语句
        """
        select = u"?o"
        sparql = None
        if slots.get('rate') is not None:
            e = u"?m :movieTitle ?o ."
            e = e + generic_movie_query(slots)
            e = e + u" ?m :movieRate ?a. Filter(?a >= {score}).".format(score=slots.get('rate'))
            sparql = SPARQL_COUNT_TEM.format(prefix=SPARQL_PREXIX, select=select, expression=e)
        return sparql

    @staticmethod
    def movie_count_lt_question(slots):
        """
        查询电影， 含小于于评分条件。 可选槽位：演员可以是多个，类型
        :param slots: 经识别后的槽位
        :return: 查询语句
        """
        select = u"?o"
        sparql = None
        if slots.get('rate') is not None:
            e = u"?m :movieTitle ?o ."
            e = e + generic_movie_query(slots)
            e = e + u" ?m :movieRate ?a. Filter(?a < {score}).".format(score=slots.get('rate'))
            sparql = SPARQL_COUNT_TEM.format(prefix=SPARQL_PREXIX, select=select, expression=e)
        return sparql

    @staticmethod
    def types_of_movie_question(slots):
        """ 
        问类型，某演员演过哪些类型的电影
        :param slots: 经识别后的槽位
        :return: 查询语句
        """

        select = u"?o"
        sparql = None
        if slots.get('pers') is not None:
            e = u"?m :hasGenre ?a. ?a :genreName ?o. "
            e = e + generic_movie_query(slots)
            sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX, select=select, expression=e)
        return sparql

    @staticmethod
    def cooperate_actors_question(slots):
        """某某合作过的演员"""
        select = u"?o"
        sparql = None
        if slots.get('pers') is not None:
            e = u"?a :personName '{person}'. ?m :hasActor ?a. ?m :hasActor ?b.  ?b :personName ?o. Filter(?o!='{person}')".format(
                person=slots.get('pers')[0])
            sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX, select=select, expression=e)
        return sparql

    # ##########################      演员基本属性查询      ###############################

    @staticmethod
    def actor_intro_question(slots):
        """
        演员简介
        :param slots: 经识别后的槽位
        :return: 查询语句
        """
        return generic_person_property(slots, 'personIntroduction')

    @staticmethod
    def actor_birthday_question(slots):
        """
        演员生日
        :param slots: 经识别后的槽位
        :return: 查询语句
        """
        return generic_person_property(slots, 'personBirthday')

    @staticmethod
    def actor_birthplace_question(slots):
        """
        演员出生地
        :param slots: 经识别后的槽位
        :return: 查询语句
        """
        return generic_person_property(slots, 'personBirthplace')

    @staticmethod
    def actor_gender_question(slots):
        """
        演员性别
        :param slots: 经识别后的槽位
        :return: 查询语句
        """
        return generic_person_property(slots, 'personGender')

    @staticmethod
    def actor_biography_question(slots):
        """
        演员星座
        :param slots: 经识别后的槽位
        :return: 查询语句
        """
        return generic_person_property(slots, 'personBiography')

    @staticmethod
    def actor_pic_question(slots):
        """
        演员头像
        :param slots: 经识别后的槽位
        :return: 查询语句
        """
        return generic_person_property(slots, 'personImage')

    @staticmethod
    def actor_englishname_question(slots):
        """
        演员英文名
        :param slots: 经识别后的槽位
        :return: 查询语句
        """
        select = u"concat( ?x1, '/ ',?x2)"
        sparql = None
        if slots.get('pers') is not None:
            e = u"?s :personName '{person}'. " \
                u"?s :personEnglishName ?x1. " \
                u"?s :personMoreFn ?x2. ".format(person=slots.get('pers')[0])

            sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX,
                                              select=select,
                                              expression=e)
            sparql = sparql.replace('DISTINCT', '')
        return sparql

    @staticmethod
    def person_alias_question(slots):
        """
        演员别名，中文别名+英文别名
        :param slots: 经识别后的槽位
        :return: 查询语句
        """
        select = u"concat( ?x1, '/ ',?x2)"
        sparql = None
        if slots.get('pers') is not None:
            e = u"?s :personName '{person}'. " \
                u"?s :personMoreCn ?x1. " \
                u"?s :personMoreFn ?x2. ".format(person=slots.get('pers')[0])

            sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX,
                                              select=select,
                                              expression=e)
            sparql = sparql.replace('DISTINCT', '')
        return sparql

    @staticmethod
    def actor_occupation_question(slots):
        """
        演员职业
        :param slots: 经识别后的槽位
        :return: 查询语句
        """
        return generic_person_property(slots, 'personOccupation')
