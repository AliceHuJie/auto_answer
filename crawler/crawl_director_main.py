# 连接本地mysql数据库

import bs4
import pymysql
import requests
from requests import TooManyRedirects

mysql_db = pymysql.connect(host="localhost", user="root", password='2736', db="anto_answer_for_movie", use_unicode=True,
                           charset="utf8")
mysql_cursor = mysql_db.cursor()
person_detail_url = 'https://movie.my_crawler.com/celebrity/{person_id}/'
insert_director_command = 'insert into `anto_answer_for_movie`.`director` (person_id, person_name, person_gender, person_english_name, person_biography, person_birth_place, person_birth_day, person_pic, person_introduction) values ({person_id}, "{person_name}", "{person_gender}", "{person_english_name}", "{person_biography}", "{person_birth_place}", "{person_birth_day}", "{person_pic}", "{person_introduction}")'
mark_person_crawled_command = 'UPDATE `anto_answer_for_movie`.`movie_to_director` SET `is_crawled`=1 WHERE `director_id`={director_id};'
mark_person_crawled_error_command = 'UPDATE `anto_answer_for_movie`.`movie_to_director` SET `is_crawled`=2 WHERE `director_id`={director_id};'


# 请求头
headers = {}
headers["Accept"] = "application/json, text/plain, */*"
headers["Accept-Encoding"] = "gzip, deflate, br"
headers["Accept-Language"] = "zh-CN,zh;q=0.8"
headers["Cache-Control"] = "max-age=0"
headers["Connection"] = "keep-alive"
# headers["Cookie"] = 'bid=b6EaQ9gcbXs; ps=y; ll="108288"; push_noty_num=0; push_doumail_num=0; _vwo_uuid_v2=D3C2FB6BD3FAD43B7C1D2B91E3CE37570|d8b98c09fe9c97032f847bee2bc98501; ap=1; ct=y; __utmv=30149280.17596; __utma=30149280.634257426.1523865856.1523960361.1523969846.6; __utmc=30149280; __utmz=30149280.1523969846.6.4.utmcsr=accounts.my_crawler.com|utmccn=(referral)|utmcmd=referral|utmcct=/safety/unlock_sms/resetpassword; __utmt=1; __utmb=30149280.1.10.1523969846; dbcl2="175968756:50qgoq3fF9c"; ck=V6_A; frodotk="36d0f6d8336d2689a472e4889a47739b"'

headers["Host"] = "movie.my_crawler.com"
headers["Referer"] = "https://movie.my_crawler.com/tag/"
# headers["Upgrade-Insecure-Requests"] = '1'
headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.90 Safari/537.36 2345Explorer/9.3.0.17248"
# proxies = {'https': 'https://223.241.78.75:18118', 'http': 'http://223.241.78.75:18118'}
proxies = {'http': 'http://proxy.baibianip.com:8000', 'https': 'https://proxy.baibianip.com:8000'}
def get_director_id_list(n):
    sql = 'SELECT director_id FROM anto_answer_for_movie.movie_to_director where is_crawled = 0 limit %d;' % n
    mysql_cursor.execute(sql)
    result = mysql_cursor.fetchall()
    movie_list = [item[0] for item in result]
    return movie_list


def craw_director_and_insert(director_id):
    try:
        director = craw_person_detail(director_id)
        insert_director_sql = insert_director_command.format(
            person_id=director["person_id"], person_name=director["person_name"],
            person_gender=director["person_gender"], person_english_name=director["person_english_name"],
            person_biography=director["person_biography"], person_birth_place=director["person_birth_place"],
            person_birth_day=director["person_birth_day"], person_pic=director["person_pic"],
            person_introduction=director["person_introduction"]
        )
        mysql_cursor.execute(insert_director_sql)
        #标记已爬过
        mark_sql = mark_person_crawled_command.format(director_id=director_id)
        # print(mark_sql)
        mysql_cursor.execute(mark_sql)
        mysql_db.commit()
    except pymysql.err.IntegrityError:
        # 标记已爬过
        mark_sql = mark_person_crawled_command.format(director_id=director_id)
        mysql_cursor.execute(mark_sql)
        mysql_db.commit()

def craw_person_detail(person_id):
    '''
    爬取演员信息存入mysql
    :param person_id:
    :return: dict
    '''

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
    resp = requests.get(url, proxies=proxies)
    # 查看响应状态码
    status_code = resp.status_code
    if status_code != 200:
        print ('Get Person Page Error' )
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
        person["person_introduction"] = ''

    name = html.h1.string
    person["person_name"] = name.split(" ")[0]
    person["person_english_name"] = " ".join(name.split(" ")[1:])
    person["person_pic"] = html.select(".article .pic ")[0].img.get("src")
    return person


if __name__ == '__main__':

    director_id_list = get_director_id_list(500)
    director_id_t = None
    try:
        for director_id in director_id_list:
            print("wil crawl director %s " % director_id)
            # print '开始爬新的導演信息'
            director_id_t = director_id
            craw_director_and_insert(director_id)
    except TooManyRedirects:
        print('ip 已封')
        exit(1)
    except:
        mysql_cursor.execute(mark_person_crawled_error_command.format(director_id=director_id_t))
        mysql_db.commit()
        # traceback.print_exc()
    finally:
        # 爬完以后关闭连接
        mysql_cursor.close()
        mysql_db.close()
