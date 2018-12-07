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


def generic_movie_property(word_objects, movie_property):
    """
    通用的查电影属性的模板
    :param word_objects: 
    :param movie_property: 
    :return: 
    """
    select = u"?x"
    sparql = None
    for w in word_objects:
        if w.pos == 'nz':
            e = u"?m :movieTitle '{movie}'." \
                u"?m :{pro} ?x".format(movie=w.token, pro=movie_property)
            sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX,
                                              select=select,
                                              expression=e)
            break
    return sparql


def generic_person_property(word_objects, person_property):
    """
    某演员的基本属性查询模板
    :param word_objects: 问句分词后的word_objects 列表，其中包含了词性
    :return: 查询语句
    """
    select = u"?x"

    sparql = None
    for w in word_objects:
        if w.pos == 'nr':
            e = u"?s :personName '{person}'." \
                u"?s :{pro} ?x".format(person=w.token, pro=person_property)

            sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX,
                                              select=select,
                                              expression=e)
            break
    return sparql


def extract_movie_person_genre(word_objects):
    """
    提取出问句中的人名，电影名。
    :param word_objects: 
    :return: 
    """
    movie = None
    person = None
    genre = None
    for w in word_objects:
        if w.pos == 'nz' and movie is None:
            movie = w.token
        if w.pos == 'nr' and person is None:
            person = w.token
        if w.pos == 'ng' and genre is None:
            genre = w.token
    return movie, person, genre


class QuestionSet:
    def __init__(self):
        pass
        # ******************************     电影基本属性查询      ********************************
    @staticmethod
    def movie_rating_question(word_objects):
        """
        某电影评分是多少
        :param word_objects: 问句分词后的word_objects 列表，其中包含了词性
        :return: 查询语句
        """
        return generic_movie_property(word_objects, 'movieRating')

    @staticmethod
    def movie_showtime_question(word_objects):
        """
        某电影上映时间是多少
        :param word_objects: 问句分词后的word_objects 列表，其中包含了词性
        :return: 查询语句
        """
        return generic_movie_property(word_objects, 'movieReleaseDate')

    @staticmethod
    def movie_intro_question(word_objects):
        """
        某电影的剧情
        :param word_objects: 问句分词后的word_objects 列表，其中包含了词性
        :return: 查询语句
        """
        return generic_movie_property(word_objects, 'movieIntroduction')

    @staticmethod
    def movie_duration_question(word_objects):
        """
        某电影时长是多少
        :param word_objects: 问句分词后的word_objects 列表，其中包含了词性
        :return: 查询语句
        """
        return generic_movie_property(word_objects, 'movieDuration')

    @staticmethod
    def movie_alias_question(word_objects):
        """
        某电影别名是什么
        :param word_objects: 问句分词后的word_objects 列表，其中包含了词性
        :return: 查询语句
        """
        return generic_movie_property(word_objects, 'movieAlias')

    @staticmethod
    def movie_cover_question(word_objects):
        """
        某电影封面是什么
        :param word_objects: 问句分词后的word_objects 列表，其中包含了词性
        :return: 查询语句
        """
        return generic_movie_property(word_objects, 'movieCover')


    # ***********************************  非基本属性查询  **************************************

    @staticmethod
    def has_actor_question(word_objects):
        """
        某电影有哪些演员
        :param word_objects:
        :return:
        """
        select = u"?x"
        sparql = None
        movie, person, genre = extract_movie_person_genre(word_objects)
        if movie is not None:
                e = u"?m :movieTitle '{movie}'." \
                    u"?m :hasActor ?a." \
                    u"?a :personName ?x".format(movie=movie)
                sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX, select=select, expression=e)
        return sparql

    @staticmethod
    def movie_show_country_question(word_objects):
        """
        电影在哪些国家上映了
        :param word_objects: 问句分词后的word_objects 列表，其中包含了词性
        :return: 查询语句
        """
        select = u"?x"

        sparql = None
        for w in word_objects:
            if w.pos == 'nz':
                e = u"?m :movieTitle '{movie}'." \
                    u"?m :showInCountry ?a." \
                    u"?a :countryName ?x".format(movie=w.token)

                sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX,
                                                  select=select,
                                                  expression=e)
                break
        return sparql

    @staticmethod
    def movie_types_question(word_objects):
        """
        电影是什么风格
        :param word_objects: 问句分词后的word_objects 列表，其中包含了词性
        :return: 查询语句
        """
        select = u"?x"

        sparql = None
        for w in word_objects:
            if w.pos == 'nz':
                e = u"?m :movieTitle '{movie}'." \
                    u"?m :hasGenre ?a." \
                    u"?a :genreName ?x".format(movie=w.token)
                sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX,
                                                  select=select,
                                                  expression=e)
                break
        return sparql

    @staticmethod
    def movie_has_director_question(word_objects):
        """
        电影有哪些导演
        :param word_objects: 问句分词后的word_objects 列表，其中包含了词性
        :return: 查询语句
        """
        select = u"?x"

        sparql = None
        for w in word_objects:
            if w.pos == 'nz':
                e = u"?m :movieTitle '{movie}'." \
                    u"?m :hasDirector ?a." \
                    u"?a :personName ?x".format(movie=w.token)

                sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX,
                                                  select=select,
                                                  expression=e)
                break
        return sparql

    @staticmethod
    def has_movie_question(word_objects):
        """
        查询电影，不包含评分条件。 可选槽位：演员可以是多个，类型
        :param word_objects: 问句分词后的word_objects 列表，其中包含了词性
        :return: 查询语句
        """
        select = u"?x"
        sparql = None
        e = ''
        i = 1
        for w in word_objects:
            if w.pos == 'nr':
                e = e + u"?s{i} :personName '{person}'. ?s{i}  :hasActedIn ?m. ".format(person=w.token, i=i)
                i = i + 1
            if w.pos == 'ng':
                e = e + u"?m :hasGenre ?g. ?g :genreName '{genre}'.".format(genre=w.token)
        if e != '':
            e = e + u" ?m :movieTitle ?x"
            sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX,
                                                  select=select,
                                                  expression=e)
        return sparql

    @staticmethod
    def has_movie_gt_question(word_objects):
        """
        查询电影， 含大于评分条件。 可选槽位：演员可以是多个，类型
        :param word_objects: 问句分词后的word_objects 列表，其中包含了词性
        :return: 查询语句
        """
        select = u"?x"
        sparql = None
        e = ''
        i = 1
        for w in word_objects:
            if w.pos == 'nr':
                e = e + u"?s{i} :personName '{person}'. ?s{i}  :hasActedIn ?m. ".format(person=w.token, i=i)
                i = i + 1
            if w.pos == 'ng':
                e = e + u"?m :hasGenre ?g. ?g :genreName '{genre}'.".format(genre=w.token)
            if w.pos == 'ss':
                e = e + u" ?m :movieRating ?r. Filter(?r >= {score}).".format(score=w.token)
        if e != '':
            e = e + u" ?m :movieTitle ?x"
            sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX,
                                                  select=select,
                                                  expression=e)
        return sparql

    @staticmethod
    def has_movie_lt_question(word_objects):
        """
        查询电影， 含小于于评分条件。 可选槽位：演员可以是多个，类型
        :param word_objects: 问句分词后的word_objects 列表，其中包含了词性
        :return: 查询语句
        """
        select = u"?x"
        sparql = None
        e = ''
        i = 1
        for w in word_objects:
            if w.pos == 'nr':
                e = e + u"?s{i} :personName '{person}'. ?s{i}  :hasActedIn ?m. ".format(person=w.token, i=i)
                i = i + 1
            if w.pos == 'ng':
                e = e + u"?m :hasGenre ?g. ?g :genreName '{genre}'.".format(genre=w.token)
            if w.pos == 'ss':
                e = e + u" ?m :movieRating ?r. Filter(?r <= {score}).".format(score=w.token)
        if e != '':
            e = e + u" ?m :movieTitle ?x"
            sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX,
                                                  select=select,
                                                  expression=e)
        return sparql

    @staticmethod
    def types_of_movie_question(word_objects):
        """ 
        问类型，某演员演过哪些类型的电影
        :param word_objects: 问句分词后的word_objects 列表，其中包含了词性
        :return: 查询语句
        """
        select = u"?x"

        sparql = None
        for w in word_objects:
            if w.pos == 'nr':
                e = u"?s :personName '{person}'." \
                    u"?s :hasActedIn ?m." \
                    u"?m :hasGenre ?a." \
                    u"?a :genreName ?x".format(person=w.token)

                sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX,
                                                  select=select,
                                                  expression=e)
                break
        return sparql

    @staticmethod
    def cooperate_actors_question(word_objects):
        """某某合作过的演员"""
        select = u"?x"
        sparql = None
        for w in word_objects:
            if w.pos == 'nr':
                e = u"?s :personName '{person}'. ?s  :hasActedIn ?m. ?m :hasActor ?a. ?a :personName ?x".format(person=w.token)
                sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX,
                                              select=select,
                                              expression=e)
                break
        return sparql
    # ##########################      演员基本属性查询      ###############################

    @staticmethod
    def actor_intro_question(word_objects):
        """
        演员简介
        :param word_objects: 问句分词后的word_objects 列表，其中包含了词性
        :return: 查询语句
        """
        return generic_person_property(word_objects, 'personIntroduction')

    @staticmethod
    def actor_birthday_question(word_objects):
        """
        演员生日
        :param word_objects: 问句分词后的word_objects 列表，其中包含了词性
        :return: 查询语句
        """
        return generic_person_property(word_objects, 'personBirthDay')

    @staticmethod
    def actor_birthplace_question(word_objects):
        """
        演员出生地
        :param word_objects: 问句分词后的word_objects 列表，其中包含了词性
        :return: 查询语句
        """
        return generic_person_property(word_objects, 'personBirthPlace')

    @staticmethod
    def actor_gender_question(word_objects):
        """
        演员性别
        :param word_objects: 问句分词后的word_objects 列表，其中包含了词性
        :return: 查询语句
        """
        return generic_person_property(word_objects, 'personGender')

    @staticmethod
    def actor_biography_question(word_objects):
        """
        演员星座
        :param word_objects: 问句分词后的word_objects 列表，其中包含了词性
        :return: 查询语句
        """
        return generic_person_property(word_objects, 'personBiography')

    @staticmethod
    def actor_pic_question(word_objects):
        """
        演员头像
        :param word_objects: 问句分词后的word_objects 列表，其中包含了词性
        :return: 查询语句
        """
        return generic_person_property(word_objects, 'personPic')

    @staticmethod
    def actor_englishname_question(word_objects):
        """
        演员头像
        :param word_objects: 问句分词后的word_objects 列表，其中包含了词性
        :return: 查询语句
        """
        return generic_person_property(word_objects, 'personEnglishName')