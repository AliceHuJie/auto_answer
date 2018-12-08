# 连接本地mysql数据库
import random
import time
import traceback

import bs4
import pymysql
import requests
from requests import TooManyRedirects

mysql_db = pymysql.connect(host="localhost", user="root", password='2736', db="anto_answer_for_movie", use_unicode=True,
                           charset="utf8")
mysql_cursor = mysql_db.cursor()
person_detail_url = 'https://movie.my_crawler.com/celebrity/{person_id}/'
insert_actor_command = 'insert into `anto_answer_for_movie`.`actor` (person_id, person_name, person_gender, person_english_name, person_biography, person_birth_place, person_birth_day, person_pic, person_introduction) values ({person_id}, "{person_name}", "{person_gender}", "{person_english_name}", "{person_biography}", "{person_birth_place}", "{person_birth_day}", "{person_pic}", "{person_introduction}")'
mark_person_crawled_command = 'UPDATE `anto_answer_for_movie`.`movie_to_actor` SET `is_crawled`=1 WHERE `actor_id`={actor_id}'
mark_person_crawled_error_command = 'UPDATE `anto_answer_for_movie`.`movie_to_actor` SET `is_crawled`=2  WHERE `actor_id`= {actor_id}'


# 请求头
headers = {}
headers["Accept"] = "application/json, text/plain, */*"
headers["Accept-Encoding"] = "gzip, deflate, br"
headers["Accept-Language"] = "zh-CN,zh;q=0.8"
headers["Cache-Control"] = "max-age=0"
headers["Connection"] = "keep-alive"
headers["Host"] = "movie.my_crawler.com"
headers[
    "Cookie"] = 'll="108288"; bid=YoMInPmOpAE; __utmc=30149280; __utmz=30149280.1524141162.1.1.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utmc=223695111; __yadk_uid=DDfMw9h7R3j01whC0PIAprcu255GiQ6h; _vwo_uuid_v2=D2CE7F8DACB2F100DAC67505F926B1DED|e92583c945a9baf837d5e9cf3f3e2000; ap=1; ps=y; __utmv=30149280.17596; ct=y; push_noty_num=0; push_doumail_num=0; __utma=30149280.325814021.1524141162.1524141162.1524192137.2; __utmt=1; __utmb=30149280.2.10.1524192137; dbcl2="175968756:u6pQzFIAtio"; ck=OkKF; __utma=223695111.1298820939.1524141163.1524143476.1524192217.3; __utmb=223695111.0.10.1524192217; __utmz=223695111.1524192217.3.2.utmcsr=my_crawler.com|utmccn=(referral)|utmcmd=referral|utmcct=/accounts/login; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1524192217%2C%22https%3A%2F%2Fwww.my_crawler.com%2Faccounts%2Flogin%3Fredir%3Dhttps%253A%252F%252Fmovie.my_crawler.com%252F%22%5D; _pk_ses.100001.4cf6=*; _pk_id.100001.4cf6=a351b8c8dc6cd472.1524141163.2.1524192224.1524143405.'
headers["Referer"] = "https://movie.my_crawler.com/tag/"
# headers["Upgrade-Insecure-Requests"] = '1'
headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.90 Safari/537.36 2345Explorer/9.3.0.17248"
# proxies = {'https': 'https://223.241.78.75:18118', 'http': 'http://223.241.78.75:18118'}
proxies = {'http': 'http://proxy.baibianip.com:8000', 'https': 'https://proxy.baibianip.com:8000'}

def get_actor_id_list(n):
    sql = 'SELECT distinct(actor_id)  FROM anto_answer_for_movie.movie_to_actor where is_crawled = 0 limit %d;' % n
    mysql_cursor.execute(sql)
    result = mysql_cursor.fetchall()
    movie_list = [item[0] for item in result]
    return movie_list


def craw_person_detail(person_id):
    '''
    爬取演员信息存入mysql
    :param person_id:
    :return: dict
    '''
    try:
        # 将一些字段初始化为空，以免信息不全，缺少字段，影响mysql的插入
        person = {
            "person_id": person_id,
            "person_gender": '',
            "person_birth_day": '',
            "person_birth_place": '',
            "person_biography": '',
            "person_introduction": '',
            "person_name": '',
            "person_english_name": '',
            "person_pic": '',
        }

        url = person_detail_url.format(person_id=person_id)
        # resp = requests.get(url, headers=headers)
        resp = requests.get(url, headers=headers)

        # 查看响应状态码
        status_code = resp.status_code
        if status_code != 200:
            print ('Get Person Page Error: %s' % status_code)
            exit(1)
            return None

        html = bs4.BeautifulSoup(resp.content.decode("utf-8"), "html.parser")
        basic_info = html.select('.info  li')

        info = {}  # 该演员含有的信息  性别 出生地 职业，可能不全
        for item in basic_info:
            ret = item.get_text().split(":")
            key = ret[0].replace("\n", '').strip()
            value = ret[1].replace("\n", '').strip()
            info[key] = value

        if u'性别' in info.keys():
            person["person_gender"] = info[u'性别']

        if u'出生日期' in info.keys():
            person["person_birth_day"] = info[u'出生日期']

        if u'出生地' in info.keys():
            person["person_birth_place"] = info[u'出生地']

        if u'星座' in info.keys():
            person["person_biography"] = info[u'星座']

        if html.find_all("span", attrs={"class": "all hidden"}):
            person["person_introduction"] = html.find_all("span", attrs={"class": "all hidden"})[0].get_text().replace("\"","\'")
        elif html.select("#intro .bd"):
            person["person_introduction"] = html.select("#intro .bd")[0].get_text().replace("\"","\'")
        else:
            person["person_introduction"]= ''
        name = html.h1.string
        person["person_name"] = name.split(" ")[0]
        person["person_english_name"] = " ".join(name.split(" ")[1:])
        person["person_pic"] = html.select(".article .pic ")[0].img.get("src")
        return person
    except AttributeError:
        traceback.print_exc()
        return None


def craw_actor_and_insert(actor_id):
    try:
        actor = craw_person_detail(actor_id)
        if actor is None:
            print('none')
            return
        insert_actor_sql = insert_actor_command.format(
            person_id=actor["person_id"], person_name=actor["person_name"],
            person_gender=actor["person_gender"], person_english_name=actor["person_english_name"],
            person_biography=actor["person_biography"], person_birth_place=actor["person_birth_place"],
            person_birth_day=actor["person_birth_day"], person_pic=actor["person_pic"],
            person_introduction=actor["person_introduction"]
        )
        #标记已爬过
        print(insert_actor_command)
        mysql_cursor.execute(insert_actor_sql)
        mark_sql = mark_person_crawled_command.format(actor_id=actor_id)
        # print(mark_sql)
        mysql_cursor.execute(mark_sql)
        mysql_db.commit()
    except pymysql.err.IntegrityError:
        #已經有的標記爲爬過
        print('爬过的')
        mark_sql = mark_person_crawled_command.format(actor_id=actor_id)
        mysql_cursor.execute(mark_sql)

if __name__ == '__main__':

    actor_id_list = get_actor_id_list(1000)
    try:
        for actor_id in actor_id_list:
            print("wil crawl actor %s " % actor_id)
            # print '开始爬新的演员信息'
            craw_actor_and_insert(actor_id)
            time.sleep(random.randint(5,10))
            # crawl_movie_and_insert_mongo(movie_id)
    except TooManyRedirects:
        print('ip 已封')
        # exit(1)
    except:
        traceback.print_exc()
    finally:
        # 爬完以后关闭连接
        mysql_cursor.close()
        mysql_db.close()
