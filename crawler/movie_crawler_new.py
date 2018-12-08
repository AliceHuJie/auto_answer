# -*- coding: utf-8 -*-
'''
    
    author: hujie
    desc: 豆瓣电影数据爬虫
    手动建立地区表和类型表
    1. 拿到所有要爬的电影url, 存入manager，后续每爬一个标记为爬过
    2. 根据电影url
        爬电影基本信息存入movie
        爬电影与类型的信息存入 movie_to_genres(movieid, genre)
        爬电影与地区的信息存入 movie_to_country(movieid, country_name)
        爬电影与演员的出演关系 存入movie_to_actor(movieid, actorid)
        爬电影与导演的关系 存入movie_to_director(movieid, directorid)
    3. 根据出演关系表，筛除去重后的演员，去爬演员信息（一个演员可能参与很多部电影，每一个电影都把所有演员爬一遍太冗余了）
    4. 根据导演关系表，导演去重去爬导演信息
    5. 根据movie_to_genres， 得到去重后的genres, 存入类型表，同时定义类型id, 更新根据movie_to_genres 为movie_id  genre_id
    6. 根据movie_to_language 同上
    6. 根据movie_to_director 同上
    
'''
import logging
import random
import re
import sys
import time
import traceback
from imp import reload

import bs4 as bs4
import pymysql
import requests
from pymongo import MongoClient
from requests import TooManyRedirects

reload(sys)


ISOTIMEFORMAT = '%Y-%m-%d %X'
logger = logging.getLogger('django')
logger2 = logging.getLogger('kbqa')
# 爬虫地址模板
search_movies_url = 'https://movie.my_crawler.com/j/new_search_subjects?sort=T&tags={tag}&genres={genres}&range=0,10&start={start}'
movie_detail_url = 'https://movie.my_crawler.com/subject/{movie_id}/'
person_detail_url = 'https://movie.my_crawler.com/celebrity/{person_id}/'
movie_cast_url = 'https://movie.my_crawler.com/subject/{movie_id}/celebrities'

chinese_pattern = re.compile(u"[\u4e00-\u9fa5]+")  # 用于查找汉字，选取演员的中文名

# 连接本地mysql数据库
mysql_db = pymysql.connect(host="localhost", user="root", password='2736', db="anto_answer_for_movie", use_unicode=True,
                           charset="utf8")
mysql_cursor = mysql_db.cursor()
#mongodb
client = MongoClient('localhost', 27017)
db = client.movie
movie_mongo_set = db.movie_info

# 插入语句模板
insert_movie_crawer_manager_command = 'INSERT INTO anto_answer_for_movie.movie_crawer_manager (movie_id, movie_name, movie_url, cover_url, rate) VALUES ( %d, "%s", "%s", "%s", %.1f)'

insert_movie_command = 'INSERT INTO `anto_answer_for_movie`.`movie`(movie_id, movie_title, movie_introduction, movie_rating, movie_release_date, movie_duration, movie_alias, movie_cover) VALUES ({movie_id}, "{movie_title}", "{movie_introduction}", {movie_rating}, "{movie_release_date}", "{movie_duration}", "{movie_alias}", "{movie_cover}");'
insert_actor_command = 'insert into `anto_answer_for_movie`.`actor` (person_id, person_name, person_gender, person_english_name, person_biography, person_birth_place, person_birth_day, person_pic, person_introduction) values ({person_id}, "{person_name}", "{person_gender}", "{person_english_name}", "{person_biography}", "{person_birth_place}", "{person_birth_day}", "{person_pic}", "{person_introduction}")'
insert_director_command = 'insert into `anto_answer_for_movie`.`director` (person_id, person_name, person_gender, person_english_name, person_biography, person_birth_place, person_birth_day, person_pic, person_introduction) values ({person_id}, "{person_name}", "{person_gender}", "{person_english_name}", "{person_biography}", "{person_birth_place}", "{person_birth_day}", "{person_pic}", "{person_introduction}")'
insert_genre_command = 'insert into genre (genre_id, genre_name) values (%s, %s)'
insert_country_command = 'insert into country (country_id, country_name) values (%s, %s)'

insert_movie_to_director_command = 'INSERT INTO `anto_answer_for_movie`.`movie_to_director`(`movie_id`,`director_id`)VALUES(%s, %s);'
insert_movie_to_actor_command = 'INSERT INTO `anto_answer_for_movie`.`movie_to_actor`(`movie_id`,`actor_id`)VALUES(%s, %s);'
insert_movie_to_genre_command = 'INSERT INTO `anto_answer_for_movie`.`movie_to_genre`(`movie_id`,`genre_name`)VALUES(%s, %s);'
insert_movie_to_country_command = 'INSERT INTO `anto_answer_for_movie`.`movie_to_country`(`movie_id`,`country_name`)VALUES(%s, %s);'
insert_movie_to_language_command = 'INSERT INTO `anto_answer_for_movie`.`movie_to_language`(`movie_id`,`language_name`)VALUES(%s, %s);'
mark_movie_crawled_command = 'UPDATE anto_answer_for_movie.movie_crawer_manager SET is_crawed = 1 WHERE movie_id={movie_id}'
mark_movie_crawled_command =  'UPDATE anto_answer_for_movie.movie_crawer_manager SET is_crawed = 1 WHERE movie_id={movie_id}'
# insert_movie_command = 'insert into movie (movie_title, movie_introduction, movie_rating, movie_id, movie_release_date) values (%s, %s, %s, %s, %s)'
# insert_person_movie_command = 'insert into person_to_movie (person_id, movie_id) values (%s, %s)'
# insert_movie_type_command = 'insert into movie_to_type (movie_id, type_id) values (%s, %s)'


# 请求头
headers = {}
headers["Accept"] = "application/json, text/plain, */*"
headers["Accept-Encoding"] = "gzip, deflate, br"
headers["Accept-Language"] = "zh-CN,zh;q=0.8"
headers["Cache-Control"] = "max-age=0"
headers["Connection"] = "keep-alive"
headers["Host"] = "movie.my_crawler.com"
headers["Referer"] = "https://movie.my_crawler.com/tag/"
headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.90 Safari/537.36 2345Explorer/9.3.0.17248"

proxies = {'http': 'http://proxy.baibianip.com:8000', 'https': 'https://proxy.baibianip.com:8000'}

USER_AGENTS = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
]

# 电影分类
const_genres_list = [u'剧情', u'喜剧', u'动作', u'爱情', u'科幻', u'悬疑', u'惊悚', u'恐怖', u'犯罪',
                     u'同性', u'音乐', u'歌舞', u'传记', u'历史', u'战争', u'西部', u'冒险', u'灾难',
                     u'武侠', u'情色']
# # 地区分类
# const_country_list = [u'中国大陆', u'美国', u'香港', u'台湾', u'日本', u'韩国', u'英国', u'法国', u'德国',
#                       u'意大利', u'西班牙', u'印度', u'泰国', u'俄罗斯', u'伊朗', u'加拿大', u'澳大利亚',
#                       u'爱尔兰', u'瑞典', u'巴西', u'丹麦']


def get_craw_movie_id_list(n):
    '''
    从数据库读出n条未爬过的电影id，然后去爬
    :return: movie_id_list
    '''
    sql = 'SELECT movie_id FROM anto_answer_for_movie.movie_crawer_manager where is_crawed=0  limit %d' % n
    mysql_cursor.execute(sql)
    result = mysql_cursor.fetchall()
    movie_list = [item[0] for item in result]
    return movie_list


def craw_movie_detail(movie_id):
    '''
    获取一个电影的基本信息
    :param movie_id: 
    :return: dict
    '''

    movie = {
        "movie_id": int(movie_id),
        "movie_title": '',
        "movie_cover": '',
        "movie_release_date": '',
        "movie_duration": '',
        "movie_alias": '',
        "movie_introduction": '',
        "genres": '',
        "countries": '',
        "languages": '',
        "movie_rating": 0,
        "director_id_list": [],
        "actor_id_list": []
    }
    try:
        url = movie_detail_url.format(movie_id=movie_id)

        resp = requests.get(url, headers=headers)

        # resp = urllib.urlopen(url, proxies=proxies)
        # resp = requests.get(url, proxies=get_proxy())
        status_code = resp.status_code  # 查看响应状态码
        if status_code != 200:
            # print 'Get Movie Page Error '
            print ('Get Movie Page Error ')
            return None

        html = bs4.BeautifulSoup(resp.content, "html.parser")
        basic_info = html.select('#info')[0]
        info = basic_info.get_text().strip().split('\n')
        # print info
        movie_info = {}  # 该演员含有的信息  性别 出生地 职业，可能不全
        for item in info:
            # print item
            ret = item.split(":")
            if len(ret) == 2:
                key = ret[0].replace("\n", '').strip()
                value = ret[1].replace("\n", '').strip()
                movie_info[key] = value
        if u'上映日期' in movie_info.keys():
            movie['movie_release_date'] = movie_info[u'上映日期']
        if u'片长' in movie_info.keys():
            movie['movie_duration'] = movie_info[u'片长']
        if u'语言' in movie_info.keys():
            languages = movie_info[u'语言'].split('/')
            movie['languages'] = [language.strip(" ") for language in languages]
        if u'制片国家/地区' in movie_info.keys():
            countries = movie_info[u'制片国家/地区'].split('/')
            movie['countries'] = [country.strip(" ") for country in countries]
        if u'类型' in movie_info.keys():
            genres_list = movie_info[u'类型'].strip().split('/')
            movie['genres'] = [genre.strip(" ") for genre in genres_list]
        if u'又名' in movie_info.keys():
            movie['movie_alias'] = movie_info[u'又名'].replace("\"", "\'")

        if html.find_all("span", attrs={"class": "all hidden"}):
            description = html.find_all("span", attrs={"class": "all hidden"})[0].get_text()
            movie['movie_introduction'] = ''.join(description.split()).replace("\"", "\'")  # 双引号转换，不然sql语句会出错
        elif html.find_all("span", attrs={"property": "v:summary"}):
            description = html.find_all("span", attrs={"property": "v:summary"})[0].get_text()
            movie["movie_introduction"] = ''.join(description.split()).replace("\"", "\'")
        else:
            movie["movie_introduction"] = ''

        movie['movie_rating'] = float(html.select('#interest_sectl .rating_num')[0].string)
        movie['movie_title'] = html.h1.span.string.split(" ")[0]  # 只取了中文标题
        movie['movie_cover'] = html.select("#mainpic")[0].img.get("src")
        # directors data(导演id列表)
        director_id_list = []
        if basic_info.select(".attrs"):
            directors_info = basic_info.select(".attrs")[0].select('a')
            for director in directors_info:
                director_url = director["href"]
                id_list = re.findall('/celebrity/(\d+)', director_url)
                if len(id_list) == 1:
                    actor_id = id_list[0]
                    director_id_list.append(actor_id)
        movie['director_id_list'] = director_id_list


        # actors data(演员id列表)
        actor_id_list = []
        if basic_info.select(".actor .attrs"):
            actors_info = basic_info.select(".actor .attrs")[0].select('a')
            for actor in actors_info:
                actor_url = actor["href"]
                id_list = re.findall('/celebrity/(\d+)', actor_url)
                if len(id_list) == 1:
                    actor_id = id_list[0]
                    actor_id_list.append(actor_id)
            movie['actor_id_list'] = actor_id_list
        return movie
    except Exception:
        traceback.print_exc()
        return None


def insert_movie(movie):
    try:
        insert_movie_sql = insert_movie_command.format(movie_id=movie['movie_id'],
                                                       movie_title=movie['movie_title'],
                                                       movie_rating=movie['movie_rating'],
                                                       movie_cover=movie['movie_cover'],
                                                       movie_alias=movie['movie_alias'],
                                                       movie_duration=movie['movie_duration'],
                                                       movie_introduction=movie['movie_introduction'],
                                                       movie_release_date=movie['movie_release_date'])
        # print(insert_movie_sql)
        mysql_cursor.execute(insert_movie_sql)
        mysql_db.commit()
        print('insert movie success')
    except:
        traceback.print_exc(file=open('error.log', 'a+'))
        print('insert movie failed， movie_id:', movie['movie_id'])


def insert_movie_to_actor(movie):
    actor_id_list = movie["actor_id_list"]
    try:
        movie_to_actor_list = [(movie_id, item) for item in actor_id_list]
        mysql_cursor.executemany(insert_movie_to_actor_command, movie_to_actor_list)
        mysql_db.commit()
        print('movie_to_actor insert success, actor_id_list:', actor_id_list)
    except:
        traceback.print_exc(file=open('error.log', 'a+'))
        print('movie_to_actor insert failed, actor_id_list:', actor_id_list)

def insert_movie_to_director(movie):
    director_id_list = movie["director_id_list"]
    try:
        movie_to_director_list = [(movie_id, item) for item in director_id_list]
        mysql_cursor.executemany(insert_movie_to_director_command, movie_to_director_list)
        mysql_db.commit()
        print('movie_to_director insert success, director_id_list:',director_id_list)
    except:
        traceback.print_exc(file=open('error.log', 'a+'))
        print('movie_to_director insert failed, director_id_list:', director_id_list)

def insert_movie_to_genre(movie):
    genres = movie["genres"]
    try:
        movie_to_genre_list = [(movie_id, genre) for genre in genres]
        mysql_cursor.executemany(insert_movie_to_genre_command, movie_to_genre_list)
        mysql_db.commit()
        print('movie_to_genre insert success, genres:', genres)
    except:
        traceback.print_exc(file=open('error.log', 'a+'))
        print('movie_to_genre insert failed, genres:', genres)

def insert_movie_to_country(movie):
    # movie_to_country 插入 TODO 去掉了外键,因为不知道有哪些国家, 同时插入的是国家名
    countries = movie["countries"]
    try:
        movie_to_country_list = [(movie_id, country) for country in countries]
        mysql_cursor.executemany(insert_movie_to_country_command, movie_to_country_list)
        mysql_db.commit()
        print ('movie_to_country insert success')
    except:
        traceback.print_exc(file=open('error.log', 'a+'))
        print('movie_to_country insert failed, contries: ',countries)

def craw_movie_and_insert(movie_id):
    '''
    传一个movie_id, 爬取相关的电影基本信息， 演员信息， 同时存入所有相关的表
    :param movie_id: 
    :return: null
    '''
    # print '#############   will  crawl movie  %d  ############' % movie_id
    print ('#############   will  crawl movie  %d  ############' % movie_id)
    try:
        movie = craw_movie_detail(movie_id)
        if movie is None:
            return
        print (movie)
        insert_movie(movie)
        insert_movie_to_actor(movie)
        insert_movie_to_director(movie)
        insert_movie_to_genre(movie)

        #try 的最后提交更新，如果出现异常，则该电影对应的所有数据都不保存, 成功保存则更新电影为已爬
        mysql_cursor.execute(mark_movie_crawled_command.format(movie_id=movie_id))
        mysql_db.commit()
    except:
        print ('[ERROR] movie %d crawl and save failed...' % movie_id)
        traceback.print_exc()
        traceback.print_exc(file=open('error.log', 'a+'))


# ******************          数据库插入辅助函数              ********************
#
# def insert_genre_info():
#     genres_list = [(genre_id, const_genres_list[genre_id]) for genre_id in range(0, len(const_genres_list))]
#     mysql_cursor.executemany(insert_genre_command, genres_list)
#     mysql_db.commit()
#
# def insert_country_info():
#     country_list = [(country_id, const_country_list[country_id]) for country_id in range(0, len(const_country_list))]
#     mysql_cursor.executemany(insert_country_command, country_list)
#     mysql_db.commit()


if __name__ == '__main__':
    # movie_id_list = get_craw_movie_id_list(500)
    #沒有country信息的

    movie_id_list = [1298584]
    try:
        for movie_id in movie_id_list:
            # print '开始爬新的电影'
            craw_movie_and_insert(movie_id)
            seconds = random.randint(5, 7)
            time.sleep(seconds)
    except TooManyRedirects:
        print ('ip 已封')
    except:
        traceback.print_exc()
    finally:
        # 爬完以后关闭连接
        mysql_cursor.close()
        mysql_db.close()
