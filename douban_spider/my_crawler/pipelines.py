import datetime
import json
import logging
import traceback

import pymysql
from scrapy.exporters import JsonItemExporter, CsvItemExporter

from douban_spider.my_crawler import settings

insert_or_update_movie_command = 'insert into movie (movie_id, title, myear, description, rate, sdate, runtime, alias, language, region, scenarists, directors, actors, rating_num, genre, update_time) VALUES ({movie_id},"{title}",{myear},"{description}",{rate},"{sdate}","{runtime}","{alias}","{language}","{region}","{scenarists}","{directors}","{actors}",{rating_num},"{genre}", "{update_time}") ON  duplicate KEY  UPDATE title = "{title}", myear = "{myear}", description="{description}", rate={rate}, sdate="{sdate}", runtime="{runtime}", alias="{alias}", language="{language}", region="{region}", scenarists="{scenarists}", directors="{directors}", actors="{actors}", rating_num={rating_num}, genre="{genre}",update_time="{update_time}";'

insert_person_command = 'REPLACE INTO person(person_id,image,cn_name, fn_name, gender,birthday,birthplace,biography,introduction,occupation,more_cn_name,more_fn_name) VALUES({person_id},"{image}","{cn_name}","{fn_name}","{gender}","{birthday}","{birthplace}","{biography}","{introduction}","{occupation}","{more_cn_name}","{more_fn_name}")'
insert_person_crawer_manager_command = 'INSERT IGNORE INTO person_crawer_manager(`person_id`)VALUES %s'  # %s可插入多条
update_person_crawled_command = 'UPDATE person_crawer_manager SET `is_crawed`=1 WHERE `person_id`={person_id}'

insert_movie_to_director_command = 'INSERT ignore INTO movie_to_director(`movie_id`,`director_id`)VALUES %s'  # %s的地方可以是多条values语句
insert_movie_to_actor_command = 'INSERT ignore INTO movie_to_actor(`movie_id`,`actor_id`)VALUES %s;'
insert_movie_to_scenarist_command = 'INSERT ignore INTO movie_to_scenarist(`movie_id`,`scenarist_id`)VALUES %s'
insert_movie_to_genre_command = 'INSERT ignore INTO movie_to_genre(`movie_id`,`genre_name`)VALUES %s'
insert_movie_to_region_command = 'INSERT ignore INTO movie_to_region(`movie_id`,`region_name`)VALUES %s'
insert_movie_to_language_command = 'INSERT ignore INTO movie_to_language(`movie_id`,`language_name`)VALUES %s'


# 这几个表是后序生成的，不需要手工插入
# insert_genre_command = 'insert ignore into genre (genre_name) values (%s)'
# insert_region_command = 'insert ignore into region (region_name) values (%s)'
# insert_language_command = 'insert ignore into language (language_name) values (%s)'

class JsonExporterPipeline(object):
    """
    导出成json文件
    """

    def __init__(self):
        self.file = open('douban_movie.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"  # 确保中文显示正常
        self.exporter.export_item(item)
        return item

    def close_spider(self, spider):
        self.exporter.finish_exporting()


class EnrolldataPipeline(object):
    """
    导出数据成csv,可以用excel打开
    """

    def open_spider(self, spider):
        self.file = open("movie.csv", "ab+")
        self.exporter = CsvItemExporter(self.file, include_headers_line=False)
        self.exporter.start_exporting()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()


class MysqlPipeline(object):
    """
    把爬取的数据存入mysql
    """

    def __init__(self):
        self.connect = pymysql.connect(
            host=settings.MYSQL_HOST,
            port=settings.PORT,
            db=settings.MYSQL_DBNAME,
            user=settings.MYSQL_USER,
            passwd=settings.MYSQL_PASSWD,
            charset='utf8',
        )
        self.cursor = self.connect.cursor()

    def process_item(self, item, spider):
        if spider.name == 'movie' or spider.name == 'movie_update':
            movie_id = int(item['id'])
            try:
                # movie info
                rate = float(item['rate']) if item['rate'] is not '' else 0  # 0表示还没有评分数据
                rating_num = int(item['rating_num']) if item['rating_num'] is not '' else 0  # 0表示暂无该项数据
                myear = int(item['year']) if item['year'] is not '' else ''
                movie_insert_or_update_sql = insert_or_update_movie_command.format(
                    movie_id=movie_id, title=item['title'],
                    myear=myear, description=item['description'],
                    rate=rate, sdate=item['date'],
                    runtime=item['runtime'], alias=item['alias'],
                    language=item['language'], region=item['region'],
                    scenarists=item['scenarist'], directors=item['director'],
                    actors=item['actor'], rating_num=rating_num,
                    genre=item['genre'], update_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )
                self.cursor.execute(movie_insert_or_update_sql)

                # movie_to_actor
                if len(item['actor_ids']) > 0:
                    multi_movie_to_actor = ''
                    for actor_id in item['actor_ids']:
                        multi_movie_to_actor += ' (%d, %d),' % (movie_id, int(actor_id))
                    movie_to_actor_insert_sql = insert_movie_to_actor_command % multi_movie_to_actor.strip(',')
                    # print(movie_to_actor_insert_sql)
                    self.cursor.execute(movie_to_actor_insert_sql)

                # movie_to_director
                if len(item['director_ids']) > 0:
                    multi_movie_to_director = ''
                    for director_id in item['director_ids']:
                        multi_movie_to_director += ' (%d, %d),' % (movie_id, int(director_id))
                    movie_to_director_insert_sql = insert_movie_to_director_command % multi_movie_to_director.strip(',')
                    # print(movie_to_director_insert_sql)
                    self.cursor.execute(movie_to_director_insert_sql)

                # movie_to_scenarist
                if len(item['scenarist_ids']) > 0:
                    multi_movie_to_scenarist = ''
                    for scenarist_id in item['scenarist_ids']:
                        multi_movie_to_scenarist += ' (%d, %d),' % (movie_id, int(scenarist_id))
                    movie_to_scenarist_insert_sql = insert_movie_to_scenarist_command % multi_movie_to_scenarist.strip(
                        ',')
                    # print(movie_to_scenarist_insert_sql)
                    self.cursor.execute(movie_to_scenarist_insert_sql)

                # movie_to_genre
                if item['genre'] is not '':
                    genre_list = item['genre'].split('/')
                    multi_movie_to_genre = ''
                    for genre in genre_list:
                        if genre.strip() is not '':
                            multi_movie_to_genre += ' (%d, "%s"),' % (movie_id, genre.strip())
                    movie_to_genre_insert_sql = insert_movie_to_genre_command % multi_movie_to_genre.strip(',')
                    # print(movie_to_genre_insert_sql)
                    self.cursor.execute(movie_to_genre_insert_sql)

                # movie_to_region
                if item['region'] is not '':
                    region_list = item['region'].split('/')
                    multi_movie_to_region = ''
                    for region in region_list:
                        if region.strip() is not '':
                            multi_movie_to_region += ' (%d, "%s"),' % (movie_id, region.strip())
                    movie_to_region_insert_sql = insert_movie_to_region_command % multi_movie_to_region.strip(',')
                    self.cursor.execute(movie_to_region_insert_sql)

                # movie_to_language
                if item['language'] is not '':
                    language_list = item['language'].split('/')
                    multi_movie_to_language = ''
                    for language in language_list:
                        if language.strip() is not '':
                            multi_movie_to_language += ' (%d, "%s"),' % (movie_id, language.strip())
                    movie_to_language_insert_sql = insert_movie_to_language_command % multi_movie_to_language.strip(',')
                    # print(movie_to_language_insert_sql)
                    self.cursor.execute(movie_to_language_insert_sql)

                # 把所有人的id存入person_crawler_manager
                person_id = set(item['actor_ids'] + item['director_ids'] + item['scenarist_ids'])
                if len(person_id) > 0:
                    multi_person_values = ''
                    for pid in person_id:
                        multi_person_values += ' (%d),' % int(pid)
                    person_manager_insert_sql = insert_person_crawer_manager_command % multi_person_values.strip(',')
                    self.cursor.execute(person_manager_insert_sql)

                self.connect.commit()
            except Exception as e:
                logging.error('[MOVIE SPIDER]: ERROR IN INSERT MOVIE %s' % movie_id)
                logging.error(traceback.print_exc(e))

        elif spider.name == 'person':
            id = item['id']
            try:
                person_insert_sql = insert_person_command.format(
                    person_id=item['id'],
                    image=item['image'],
                    cn_name=item['cn_name'],
                    fn_name=item['fn_name'],
                    gender=item['gender'],
                    birthday=item['birthday'],
                    birthplace=item['birthplace'],
                    biography=item['biography'],
                    introduction=item['introduction'],
                    occupation=item['occupation'],
                    more_cn_name=item['more_cn_name'],
                    more_fn_name=item['more_fn_name'],
                )
                # print(person_insert_sql)
                self.cursor.execute(person_insert_sql)
                self.cursor.execute(update_person_crawled_command.format(person_id=id))
                self.connect.commit()
            except Exception as e:
                logging.error('[PERSON SPIDER]: ERROR IN INSERT PERSON : %s' % id)
                logging.error(traceback.print_exc(e))
        else:
            pass
        return item

    def close_spider(self, spider):
        self.cursor.close()
        self.connect.close()
