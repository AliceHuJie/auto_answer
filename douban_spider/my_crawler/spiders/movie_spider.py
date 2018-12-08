# -*- coding: utf-8 -*-
# @Time    : 2018/12/8 12:44
# @Author  : hujie
# @Info  : 文件说明
import json
import logging
from urllib import parse

from scrapy import Request, Selector, Spider

from douban_spider.my_crawler.items import *
# mongo数据库
from douban_spider.my_crawler.settings import DEFAULT_REQUEST_HEADERS

start = 0  # 起始页面


class MovieSpider(Spider):
    name = "movie"
    allowed_domains = ["movie.douban.com"]
    film_listurl = 'https://movie.douban.com/j/new_search_subjects?sort={sorttype}&range=0,10&tags=%E7%94%B5%E5%BD%B1&start={page}&countries={country}'
    film_url = 'https://movie.douban.com/subject/{id}/'
    # 可选择的地区：中国大陆 美国 香港 台湾 日本 韩国 英国 法国 德国 意大利 西班牙 印度 泰国 俄罗斯 伊朗 加拿大 澳大利亚 爱尔兰 瑞典 巴西 丹麦
    countrylist = ['中国大陆', '香港', '台湾']
    year_list = range(1990, 2008)
    # 可选择的排序方法
    # U近期热门，S评分最高，R最新上映，T标记最多
    sortlist = ['U', 'S', 'R', 'T']

    def start_requests(self):
        for sorttype in self.sortlist[:1]:
            for country in self.countrylist[:1]:
                country = parse.quote(country)
                for i in range(1, 2):
                    start = i * 20
                    yield Request(self.film_listurl.format(page=start, country=country, sorttype=sorttype),
                                  headers=DEFAULT_REQUEST_HEADERS,
                                  callback=self.parse)

    def parse(self, response):
        """
        解析页面，获取电影id，构造电影链接
        :param response: Response对象
        :return:
        """
        self.logger.debug(response)
        result = json.loads(response.text)
        if result.get('data'):
            filmlist = result.get('data')
            if filmlist != []:
                for film in filmlist:
                    id = film.get('id')  # 获取电影id
                    title = film.get('title')
                    logging.getLogger(__name__).debug("已获取电影id：%s %s" % (title, id))
                    yield Request(self.film_url.format(id=id), callback=self.parse_film, meta={'id': id})

    def parse_film(self, response):
        """
        解析单部电影详情信息
        :param response: Response对象
        :return:
        """
        selector = Selector(response=response)
        # id
        id = response.meta.get('id')
        # 电影名字
        title = selector.xpath('//span[@property="v:itemreviewed"]/text()').extract()[0]
        # 年份
        try:
            year = selector.xpath('//*[@id="content"]/h1/span[2]/text()').extract()[0][1:5]
        except IndexError:
            year = None
        # 制片国家
        region = selector.xpath('//*[@id="info"]').re('制片国家/地区:</span>\s(.*)<br>')
        # 语言
        language = selector.xpath('//*[@id="info"]').re('语言:</span>\s(.*)<br>')
        # 导演
        director = selector.xpath('//*[@rel="v:directedBy"]/text()').extract()
        # 类型
        type = selector.xpath('//*[@property="v:genre"]/text()').extract()
        # 演员
        actor = selector.xpath('//*[@rel="v:starring"]/text()').extract()
        # 上映日期
        date = selector.xpath('//span[@property="v:initialReleaseDate"]/text()').extract()
        # 片长
        runtime = selector.xpath('//span[@property="v:runtime"]/text()').extract()
        # 评分
        try:
            rate = selector.xpath('//strong[@property="v:average"]/text()').extract()[0]
        except IndexError:
            rate = None
        # 评价人数
        try:
            rating_num = selector.xpath('//span[@property="v:votes"]/text()').extract()[0]
        except IndexError:
            rating_num = None

        film_info_item = MovieItem()

        field_map = {
            'id': id, 'title': title, 'year': year, 'region': region, 'language': language,
            'director': director, 'type': type, 'actor': actor, 'date': date,
            'runtime': runtime, 'rate': rate, 'rating_num': rating_num
        }

        for field, attr in field_map.items():
            film_info_item[field] = attr

        yield film_info_item
