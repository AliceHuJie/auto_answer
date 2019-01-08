# -*- coding: utf-8 -*-
# @Time    : 2019/1/2 17:34
# @Author  : hujie
# @Info  : 文件说明

# -*- coding: utf-8 -*-
# @Time    : 2018/12/8 12:44
# @Author  : hujie
# @Info  : 从movie_crawer

import json
import logging
from urllib import parse

from scrapy import Request, Spider

from douban_spider.my_crawler.items import *
from douban_spider.my_crawler.settings import DEFAULT_REQUEST_HEADERS

year_list = list(range(2018, 1990, -1))
country_list = [u'中国大陆', u'美国', u'香港', u'台湾', u'日本', u'韩国', u'英国', u'法国', u'德国', u'意大利', u'西班牙', u'印度', u'泰国', u'俄罗斯',
                u'伊朗', u'加拿大',
                u'澳大利亚', u'爱尔兰', u'瑞典', u'巴西', u'丹麦']


class MovieListSpider(Spider):
    name = "movie_list"
    allowed_domains = ["movie.douban.com"]
    # sort = R 按上映时间逆序
    film_listurl = 'https://movie.douban.com/j/new_search_subjects?sort=U&range=0,10&tags={tag}&start={page}&countries={country}&year_range={year},{year}'
    film_url = 'https://movie.douban.com/subject/{id}/'
    tag = parse.quote('电影')

    def start_requests(self):
        print('Movie List Spider Start ...')
        logging.info('Movie List Spider Start ...')
        for country in country_list[:1]:  # 国家在前，先爬完一个国家所有年份的电影
            c = parse.quote(country)
            for year in year_list[12:]:  # len(year_list)
                for page in range(0, 200):
                    # logging.warn('country:' + country + ' year:' + str(year) + ' page:' + str(page))
                    start = page * 20
                    yield Request(self.film_listurl.format(tag=self.tag, country=c, year=year, page=start),
                                  headers=DEFAULT_REQUEST_HEADERS,
                                  callback=self.parse, meta={'year': year, 'country': country})

    def parse(self, response):
        """
        解析页面，获取电影id，构造电影链接
        :param response: Response对象
        :return:
        """
        self.logger.debug(response)
        result = json.loads(response.text)
        if result.get('data'):
            film_list = result.get('data')
            if film_list is not []:
                for film in film_list:
                    id = film.get('id')  # 获取电影id
                    title = film.get('title')
                    item = MvItem()
                    item['id'] = id
                    item['title'] = title.replace('\'', '')
                    item['year'] = response.meta.get('year')
                    item['country'] = response.meta.get('country')
                    print(id + '  ' + title)
                    yield item
