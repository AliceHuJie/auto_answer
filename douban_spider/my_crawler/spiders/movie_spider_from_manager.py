# -*- coding: utf-8 -*-
# @Time    : 2018/12/8 12:44
# @Author  : hujie
# @Info  : 从movie_crawer

import logging

import pymysql
from scrapy import Request, Spider

from douban_spider.my_crawler import settings
from douban_spider.my_crawler.settings import DEFAULT_REQUEST_HEADERS
from douban_spider.my_crawler.spiders.movie_spider import MovieSpider

year_list = list(range(2018, 1990, -1))
country_list = [u'中国大陆', u'美国', u'香港', u'台湾', u'日本', u'韩国', u'英国', u'法国', u'德国', u'意大利', u'西班牙', u'印度', u'泰国', u'俄罗斯',
                u'伊朗', u'加拿大',
                u'澳大利亚', u'爱尔兰', u'瑞典', u'巴西', u'丹麦']


class MovieFromManagerSpider(Spider):
    name = "movie_from_manager"

    allowed_domains = ["movie.douban.com"]
    movie_url = 'https://movie.douban.com/subject/{id}/'
    connect = pymysql.connect(
        host=settings.MYSQL_HOST,
        port=settings.PORT,
        db=settings.MYSQL_DBNAME,
        user=settings.MYSQL_USER,
        passwd=settings.MYSQL_PASSWD,
        charset='utf8',
    )
    cursor = connect.cursor()

    def start_requests(self):
        print('Movie from manager Spider Start ...')
        logging.info('Movie from manager Spider Start ...')
        movie_ids_query = 'SELECT id FROM movie_crawer_manager where is_crawed = 0'
        count = self.cursor.execute(movie_ids_query)
        if count == 0:
            print('No movie to Crawl, Spider Stop ...')
            logging.info('No movie to Crawl, Spider Stop ...')
            return
        for i in range(count):
            movie_id = self.cursor.fetchone()[0]  # fetchone 得到的是一个一个元素的tuple
            # movie_id = 1054531  # 用于debug
            yield Request(self.movie_url.format(id=movie_id), headers=DEFAULT_REQUEST_HEADERS, callback=self.parse_film,
                          meta={'id': movie_id})

    def parse_film(self, response):
        # 与之前的电影页面解析相同，就不需要维护两份了
        MovieSpider().parse_film(response)
